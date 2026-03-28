import os
import sqlite3
from pathlib import Path

import bcrypt

_BACKEND_DIR = Path(__file__).resolve().parent.parent


def get_db_path() -> Path:
    override = os.environ.get("PORTAL_DB_PATH")
    if override:
        return Path(override)
    return _BACKEND_DIR / "data" / "portal.sqlite"


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
