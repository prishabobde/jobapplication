import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt

from .demo_applicants_data import DEMO_APPLICANTS
from .jobs_data import JOB_SEEDS

_BACKEND_DIR = Path(__file__).resolve().parent.parent

SOHUM_SAMPLE_RESUME = """SOHUM K.
Sample resume (seed data for Prisha Company portal)

EXPERIENCE
• Built internal tools and dashboards in a collaborative team environment.
• Comfortable with Python, data analysis, and clear written communication.

EDUCATION
• B.S. Computer Science (example)

This file was generated automatically for the demo user "sohum" applying to two open roles.
"""


def get_db_path() -> Path:
    override = os.environ.get("PORTAL_DB_PATH")
    if override:
        return Path(override)
    return _BACKEND_DIR / "data" / "portal.sqlite"


def get_resumes_dir() -> Path:
    d = get_db_path().parent / "resumes"
    d.mkdir(parents=True, exist_ok=True)
    return d


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
    except ValueError:
        return False


def get_conn() -> sqlite3.Connection:
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _migrate_users_table(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    ).fetchone()
    if not row:
        return
    cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "email" in cols and "username" not in cols:
        conn.execute("ALTER TABLE users RENAME COLUMN email TO username")
        conn.commit()


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('hr', 'applicant')),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()
        _migrate_users_table(conn)

        hr_count = conn.execute("SELECT COUNT(*) AS n FROM users WHERE role = 'hr'").fetchone()["n"]
        if hr_count == 0:
            h = hash_password("hr")
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'hr')",
                ("hr", h),
            )
            conn.commit()

        if not conn.execute("SELECT 1 FROM users WHERE username = ?", ("prisha",)).fetchone():
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'hr')",
                ("prisha", hash_password("prisha")),
            )
            conn.commit()

        app_count = conn.execute(
            "SELECT COUNT(*) AS n FROM users WHERE role = 'applicant'"
        ).fetchone()["n"]
        if app_count == 0:
            h = hash_password("applicant")
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'applicant')",
                ("applicant", h),
            )
            conn.commit()

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                department TEXT,
                location TEXT,
                employment_type TEXT,
                is_open INTEGER NOT NULL DEFAULT 1 CHECK (is_open IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()

        job_count = conn.execute("SELECT COUNT(*) AS n FROM jobs").fetchone()["n"]
        if job_count == 0:
            conn.executemany(
                """
                INSERT INTO jobs (title, description, department, location, employment_type)
                VALUES (?, ?, ?, ?, ?)
                """,
                JOB_SEEDS,
            )
            conn.commit()

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                applicant_id INTEGER NOT NULL,
                stored_filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (job_id) REFERENCES jobs(id),
                FOREIGN KEY (applicant_id) REFERENCES users(id),
                UNIQUE(job_id, applicant_id)
            );
            """
        )
        conn.commit()

        _seed_sohum_sample_applications(conn)
        _seed_demo_applicants_bulk(conn)


def _seed_sohum_sample_applications(conn: sqlite3.Connection) -> None:
    """Demo applicant with resumes on the first two open jobs (by id)."""
    row = conn.execute("SELECT id FROM users WHERE username = ?", ("sohum",)).fetchone()
    if not row:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'applicant')",
            ("sohum", hash_password("sohum")),
        )
        conn.commit()
        sohum_id = int(cur.lastrowid)
    else:
        sohum_id = int(row["id"])

    resume_dir = get_resumes_dir()
    old_ts = (datetime.now(timezone.utc) - timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")
    job_rows = conn.execute("SELECT id FROM jobs ORDER BY id ASC LIMIT 2").fetchall()
    for jr in job_rows:
        job_id = int(jr["id"])
        exists = conn.execute(
            "SELECT 1 FROM applications WHERE job_id = ? AND applicant_id = ?",
            (job_id, sohum_id),
        ).fetchone()
        if exists:
            continue
        stored = f"seed_sohum_{job_id}_{uuid.uuid4().hex}.txt"
        (resume_dir / stored).write_text(SOHUM_SAMPLE_RESUME, encoding="utf-8")
        conn.execute(
            """
            INSERT INTO applications (job_id, applicant_id, stored_filename, original_filename, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (job_id, sohum_id, stored, "Sohum_Sample_Resume.txt", old_ts),
        )
        conn.commit()


def _seed_demo_applicants_bulk(conn: sqlite3.Connection) -> None:
    """Additional demo applicants so HR usually sees 5+ per popular job."""
    job_ids = [int(r["id"]) for r in conn.execute("SELECT id FROM jobs ORDER BY id ASC").fetchall()]
    if not job_ids:
        return
    resume_dir = get_resumes_dir()
    now = datetime.now(timezone.utc)

    for i, (username, password, job_off, resume_body, orig_name) in enumerate(DEMO_APPLICANTS):
        if job_off >= len(job_ids):
            continue
        job_id = job_ids[job_off]
        row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'applicant')",
                (username, hash_password(password)),
            )
            conn.commit()
            uid = int(cur.lastrowid)
        else:
            uid = int(row["id"])

        exists = conn.execute(
            "SELECT 1 FROM applications WHERE job_id = ? AND applicant_id = ?",
            (job_id, uid),
        ).fetchone()
        if exists:
            continue

        stored = f"seed_demo_{username}_{job_id}_{uuid.uuid4().hex}.txt"
        (resume_dir / stored).write_text(resume_body, encoding="utf-8")
        created = (now - timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """
            INSERT INTO applications (job_id, applicant_id, stored_filename, original_filename, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (job_id, uid, stored, orig_name, created),
        )
        conn.commit()
