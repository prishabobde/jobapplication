from contextlib import asynccontextmanager
import logging
import re
import sqlite3
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from .auth import create_token, safe_decode
from .config import settings
from .database import get_conn, get_resumes_dir, hash_password, init_db, verify_password
from .resume_extract import extract_resume_text
from .schemas import (
    AuthResponse,
    HrApplicantResumeResponse,
    JobApplicantOut,
    JobApplicantsResponse,
    JobOut,
    JobsListResponse,
    LoginBody,
    MeResponse,
    MyApplicationOut,
    RegisterBody,
    ResumeSummariesResponse,
    ResumeSummaryItem,
    TopPickOut,
    ResumeUploadResponse,
    UserOut,
)
from .summarize_resumes import summarize_top_applicants

RESUME_MAX_BYTES = 5 * 1024 * 1024
RESUME_SUFFIXES = {".pdf", ".doc", ".docx", ".txt"}
SAFE_FILENAME_RE = re.compile(r"[^a-zA-Z0-9._\- ]+")

log = logging.getLogger("prisha.portal")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Prisha Company Portal API", lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_error(_request, exc: HTTPException):
    detail = exc.detail
    msg = detail if isinstance(detail, str) else str(detail)
    return JSONResponse(status_code=exc.status_code, content={"error": msg})

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Lightweight 200 for platform health checks that probe `/`."""
    return {"ok": True, "service": "prisha-portal-api"}


@app.get("/api/health")
def health():
    return {"ok": True, "service": "prisha-portal-api"}


@app.post("/api/auth/register", response_model=AuthResponse, status_code=201)
def register(body: RegisterBody):
    if body.role != "applicant":
        raise HTTPException(status_code=403, detail="Only applicants can self-register")
    username = body.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="username is required")
    password_hash = hash_password(body.password)
    try:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, "applicant"),
            )
            conn.commit()
            user_id = int(cur.lastrowid)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Username already taken") from None

    token = create_token(user_id, username, "applicant")
    return AuthResponse(
        token=token,
        user=UserOut(id=user_id, username=username, role="applicant"),
    )


@app.post("/api/auth/login", response_model=AuthResponse)
def login(body: LoginBody):
    if body.role not in ("hr", "applicant"):
        raise HTTPException(status_code=400, detail="role must be hr or applicant")
    username = body.username.strip()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if not row or row["role"] != body.role:
        raise HTTPException(status_code=401, detail="Invalid credentials or role")
    if not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials or role")

    token = create_token(row["id"], row["username"], row["role"])
    return AuthResponse(
        token=token,
        user=UserOut(id=row["id"], username=row["username"], role=row["role"]),
    )


def bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing token")
    return parts[1].strip()


def auth_payload(token: str = Depends(bearer_token)) -> dict:
    payload = safe_decode(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


def require_hr(payload: dict = Depends(auth_payload)) -> dict:
    if str(payload.get("role")) != "hr":
        raise HTTPException(status_code=403, detail="HR access required")
    return payload


def require_applicant(payload: dict = Depends(auth_payload)) -> dict:
    if str(payload.get("role")) != "applicant":
        raise HTTPException(status_code=403, detail="Applicant access required")
    return payload


@app.get("/api/auth/me", response_model=MeResponse)
def me(payload: dict = Depends(auth_payload)):
    uname = payload.get("username") or payload.get("email")
    if not uname:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return MeResponse(
        user=UserOut(
            id=int(payload["sub"]),
            username=str(uname),
            role=str(payload["role"]),
        )
    )


def _job_from_row(row: sqlite3.Row) -> JobOut:
    return JobOut(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        department=row["department"],
        location=row["location"],
        employment_type=row["employment_type"],
        is_open=bool(row["is_open"]),
        created_at=row["created_at"],
    )


@app.get("/api/jobs", response_model=JobsListResponse)
def list_jobs(_payload: dict = Depends(auth_payload)):
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, title, description, department, location, employment_type, is_open, created_at
            FROM jobs
            WHERE is_open = 1
            ORDER BY id
            """
        ).fetchall()
    return JobsListResponse(jobs=[_job_from_row(r) for r in rows])


@app.get("/api/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, _payload: dict = Depends(auth_payload)):
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, title, description, department, location, employment_type, is_open, created_at
            FROM jobs
            WHERE id = ? AND is_open = 1
            """,
            (job_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_from_row(row)


def _assert_open_job(conn: sqlite3.Connection, job_id: int) -> None:
    row = conn.execute(
        "SELECT id FROM jobs WHERE id = ? AND is_open = 1",
        (job_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")


def _upsert_job_application_resume(
    conn: sqlite3.Connection,
    resume_dir: Path,
    job_id: int,
    applicant_id: int,
    content: bytes,
    orig_name: str,
) -> tuple[int, str, str]:
    """Insert or update the application row for this job + applicant; write new file, remove old file."""
    if len(content) > RESUME_MAX_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    suffix = Path(orig_name).suffix.lower()
    if suffix not in RESUME_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail="Allowed file types: .pdf, .doc, .docx, .txt",
        )
    stored = f"{uuid.uuid4().hex}{suffix}"
    dest = resume_dir / stored
    if dest.exists():
        raise HTTPException(status_code=500, detail="Storage conflict; retry")

    display_name = SAFE_FILENAME_RE.sub("_", orig_name).strip() or f"resume{suffix}"

    old = conn.execute(
        "SELECT id, stored_filename FROM applications WHERE job_id = ? AND applicant_id = ?",
        (job_id, applicant_id),
    ).fetchone()
    if old:
        old_path = resume_dir / old["stored_filename"]
        if old_path.is_file():
            old_path.unlink()

    dest.write_bytes(content)

    if old:
        conn.execute(
            """
            UPDATE applications
            SET stored_filename = ?, original_filename = ?, created_at = datetime('now')
            WHERE id = ?
            """,
            (stored, display_name, old["id"]),
        )
        app_id = int(old["id"])
    else:
        cur = conn.execute(
            """
            INSERT INTO applications (job_id, applicant_id, stored_filename, original_filename)
            VALUES (?, ?, ?, ?)
            """,
            (job_id, applicant_id, stored, display_name),
        )
        app_id = int(cur.lastrowid)

    row = conn.execute(
        "SELECT created_at FROM applications WHERE id = ?",
        (app_id,),
    ).fetchone()
    return app_id, display_name, str(row["created_at"])


@app.get("/api/jobs/{job_id}/applicants", response_model=JobApplicantsResponse)
def list_job_applicants(
    job_id: int,
    limit: int = 5,
    _hr: dict = Depends(require_hr),
):
    limit = min(max(limit, 1), 5)
    with get_conn() as conn:
        _assert_open_job(conn, job_id)
        rows = conn.execute(
            """
            SELECT a.id AS application_id, a.applicant_id, u.username,
                   a.original_filename, a.created_at AS applied_at
            FROM applications a
            JOIN users u ON u.id = a.applicant_id
            WHERE a.job_id = ?
            ORDER BY datetime(a.created_at) DESC
            LIMIT ?
            """,
            (job_id, limit),
        ).fetchall()
    return JobApplicantsResponse(
        applicants=[
            JobApplicantOut(
                application_id=r["application_id"],
                applicant_id=r["applicant_id"],
                username=r["username"],
                original_filename=r["original_filename"],
                applied_at=r["applied_at"],
            )
            for r in rows
        ]
    )


@app.post("/api/jobs/{job_id}/summarize-resumes", response_model=ResumeSummariesResponse)
async def summarize_job_resumes(job_id: int, _hr: dict = Depends(require_hr)):
    """HR only: load top 5 applicants’ resume text and ask OpenAI for short summaries."""
    model = (settings.openai_model or "gpt-5-nano").strip()
    with get_conn() as conn:
        _assert_open_job(conn, job_id)
        job_row = conn.execute(
            "SELECT title, description FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()
        job_title = str(job_row["title"]) if job_row else ""
        job_description = str(job_row["description"]) if job_row else ""
        rows = conn.execute(
            """
            SELECT a.id AS application_id, u.username, a.stored_filename
            FROM applications a
            JOIN users u ON u.id = a.applicant_id
            WHERE a.job_id = ?
            ORDER BY datetime(a.created_at) DESC
            LIMIT 5
            """,
            (job_id,),
        ).fetchall()

    if not rows:
        return ResumeSummariesResponse(summaries=[], top_pick=None, model=model)

    api_key = settings.openai_api_key.get_secret_value().strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OpenAI is not configured. Set OPENAI_API_KEY in the backend .env file.",
        )

    resume_dir = get_resumes_dir()
    blocks: list[tuple[int, str, str]] = []
    for r in rows:
        path = resume_dir / r["stored_filename"]
        text = extract_resume_text(path)
        blocks.append((int(r["application_id"]), r["username"], text))

    try:
        ai_out = await summarize_top_applicants(
            api_key=api_key,
            model=model,
            job_title=job_title,
            job_description=job_description,
            blocks=blocks,
        )
        raw_items = ai_out.get("summaries") or []
        raw_top = ai_out.get("top_pick")
    except Exception as exc:  # noqa: BLE001
        # Do not return exception text to clients — it can occasionally include request metadata.
        log.exception("OpenAI resume summarization failed")
        raise HTTPException(
            status_code=502,
            detail="Could not generate summaries. Check server logs or try again later.",
        ) from exc

    by_id = {int(x["application_id"]): x for x in raw_items if isinstance(x, dict) and "application_id" in x}
    summaries: list[ResumeSummaryItem] = []
    for app_id, username, _ in blocks:
        hit = by_id.get(app_id)
        if hit and isinstance(hit.get("summary"), str):
            summaries.append(
                ResumeSummaryItem(
                    application_id=app_id,
                    username=str(hit.get("username", username)),
                    summary=hit["summary"],
                )
            )
        else:
            summaries.append(
                ResumeSummaryItem(
                    application_id=app_id,
                    username=username,
                    summary="(No summary returned for this applicant.)",
                )
            )

    top_pick: TopPickOut | None = None
    if isinstance(raw_top, dict) and raw_top.get("reason"):
        try:
            tid = int(raw_top["application_id"])
            block_usernames = {b[0]: b[1] for b in blocks}
            if tid in block_usernames:
                top_pick = TopPickOut(
                    application_id=tid,
                    username=str(raw_top.get("username", block_usernames[tid])),
                    reason=str(raw_top.get("reason", "")),
                )
        except (KeyError, TypeError, ValueError):
            top_pick = None

    return ResumeSummariesResponse(summaries=summaries, top_pick=top_pick, model=model)


@app.get("/api/jobs/{job_id}/my-application", response_model=MyApplicationOut)
def get_my_application(job_id: int, payload: dict = Depends(require_applicant)):
    applicant_id = int(payload["sub"])
    with get_conn() as conn:
        _assert_open_job(conn, job_id)
        row = conn.execute(
            """
            SELECT id AS application_id, original_filename, created_at AS applied_at
            FROM applications
            WHERE job_id = ? AND applicant_id = ?
            """,
            (job_id, applicant_id),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No application for this job")
    return MyApplicationOut(
        application_id=row["application_id"],
        original_filename=row["original_filename"],
        applied_at=row["applied_at"],
    )


@app.post("/api/jobs/{job_id}/resume", response_model=ResumeUploadResponse)
async def upload_resume(
    job_id: int,
    payload: dict = Depends(require_applicant),
    file: UploadFile = File(...),
):
    applicant_id = int(payload["sub"])
    content = await file.read()
    orig_name = file.filename or "resume"
    resume_dir = get_resumes_dir()
    with get_conn() as conn:
        _assert_open_job(conn, job_id)
        app_id, display_name, applied_at = _upsert_job_application_resume(
            conn, resume_dir, job_id, applicant_id, content, orig_name
        )
        conn.commit()

    return ResumeUploadResponse(
        application_id=app_id,
        original_filename=display_name,
        applied_at=applied_at,
    )


@app.post("/api/jobs/{job_id}/hr-applicant-resume", response_model=HrApplicantResumeResponse)
async def hr_submit_applicant_resume(
    job_id: int,
    _hr: dict = Depends(require_hr),
    username: str = Form(),
    file: UploadFile = File(...),
    password: str | None = Form(default=None),
):
    """
    HR: create applicant user if username is new, then attach/replace resume for this job.
    If the applicant already exists, only the resume for this role is replaced (password unchanged).
    Optional password (defaults to username) is used only when creating the user.
    """
    uname = username.strip()
    if not uname:
        raise HTTPException(status_code=400, detail="username is required")
    content = await file.read()
    orig_name = file.filename or "resume"
    resume_dir = get_resumes_dir()

    with get_conn() as conn:
        _assert_open_job(conn, job_id)
        row = conn.execute(
            "SELECT id, role FROM users WHERE username = ?",
            (uname,),
        ).fetchone()
        created_new = False
        if row:
            if row["role"] != "applicant":
                raise HTTPException(
                    status_code=400,
                    detail="That username is already used for a non-applicant account.",
                )
            applicant_id = int(row["id"])
        else:
            raw_pw = password.strip() if password and password.strip() else uname
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (uname, hash_password(raw_pw), "applicant"),
            )
            applicant_id = int(cur.lastrowid)
            created_new = True

        app_id, display_name, applied_at = _upsert_job_application_resume(
            conn, resume_dir, job_id, applicant_id, content, orig_name
        )
        conn.commit()

    return HrApplicantResumeResponse(
        application_id=app_id,
        applicant_id=applicant_id,
        username=uname,
        original_filename=display_name,
        applied_at=applied_at,
        created_new_user=created_new,
    )


@app.get("/api/applications/{application_id}/resume")
def download_resume(application_id: int, payload: dict = Depends(auth_payload)):
    role = str(payload.get("role"))
    user_id = int(payload["sub"])
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT a.applicant_id, a.stored_filename, a.original_filename
            FROM applications a
            WHERE a.id = ?
            """,
            (application_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")
    if role != "hr" and user_id != int(row["applicant_id"]):
        raise HTTPException(status_code=403, detail="Not allowed to download this resume")

    stored = row["stored_filename"]
    if "/" in stored or "\\" in stored or ".." in stored:
        raise HTTPException(status_code=500, detail="Invalid storage path")

    path = get_resumes_dir() / stored
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Resume file missing")

    return FileResponse(
        path,
        filename=row["original_filename"],
        media_type="application/octet-stream",
    )
