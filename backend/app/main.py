from contextlib import asynccontextmanager
import sqlite3

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .auth import create_token, safe_decode
from .config import settings
from .database import get_conn, hash_password, init_db, verify_password
from .schemas import AuthResponse, LoginBody, MeResponse, RegisterBody, UserOut


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
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/api/auth/me", response_model=MeResponse)
def me(token: str = Depends(bearer_token)):
    payload = safe_decode(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
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
