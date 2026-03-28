from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from .config import settings


def _secret() -> str:
    s = settings.jwt_secret
    if not s or len(s) < 16:
        raise RuntimeError("Set JWT_SECRET (min 16 chars) in backend/.env")
    return s


def create_token(user_id: int, username: str, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=7)
    exp_ts = int(exp.timestamp())
    # python-jose requires string "sub" when verifying JWTs
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": exp_ts,
    }
    return jwt.encode(payload, _secret(), algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=["HS256"])


def safe_decode(token: str) -> dict | None:
    try:
        return decode_token(token)
    except JWTError:
        return None
