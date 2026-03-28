import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PORTAL_DB_PATH", str(tmp_path / "portal.sqlite"))
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-key-32chars!!")
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://localhost:5173")

    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as tc:
        yield tc
