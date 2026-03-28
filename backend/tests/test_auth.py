def test_login_hr_demo_simple(client):
    r = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    assert data["user"]["id"] == 1
    assert data["user"]["username"] == "hr"
    assert data["user"]["role"] == "hr"


def test_login_hr_prisha(client):
    r = client.post(
        "/api/auth/login",
        json={"username": "prisha", "password": "prisha", "role": "hr"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["username"] == "prisha"
    assert data["user"]["role"] == "hr"


def test_login_applicant_demo_simple(client):
    r = client.post(
        "/api/auth/login",
        json={"username": "applicant", "password": "applicant", "role": "applicant"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["username"] == "applicant"
    assert data["user"]["role"] == "applicant"


def test_login_wrong_password(client):
    r = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "wrong", "role": "hr"},
    )
    assert r.status_code == 401
    assert r.json()["error"] == "Invalid credentials or role"


def test_login_wrong_role(client):
    r = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "applicant"},
    )
    assert r.status_code == 401


def test_register_applicant_any_username_password(client):
    r = client.post(
        "/api/auth/register",
        json={"username": "x", "password": "1", "role": "applicant"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["user"]["username"] == "x"
    assert data["user"]["role"] == "applicant"
    assert data["token"]


def test_register_applicant_username_trimmed(client):
    r = client.post(
        "/api/auth/register",
        json={"username": "  bob  ", "password": "p", "role": "applicant"},
    )
    assert r.status_code == 201
    assert r.json()["user"]["username"] == "bob"


def test_register_hr_forbidden(client):
    r = client.post(
        "/api/auth/register",
        json={"username": "evil", "password": "p", "role": "hr"},
    )
    assert r.status_code == 403
    assert "applicant" in r.json()["error"].lower()


def test_register_duplicate_username(client):
    body = {"username": "dup", "password": "a", "role": "applicant"}
    assert client.post("/api/auth/register", json=body).status_code == 201
    r2 = client.post("/api/auth/register", json=body)
    assert r2.status_code == 409
    assert "taken" in r2.json()["error"].lower()


def test_me_with_valid_token(client):
    login = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    ).json()
    r = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login['token']}"},
    )
    assert r.status_code == 200
    assert r.json()["user"]["username"] == "hr"


def test_me_missing_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_invalid_token(client):
    r = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert r.status_code == 401


def test_login_invalid_role(client):
    r = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "admin"},
    )
    assert r.status_code == 400


def test_register_whitespace_only_username_rejected(client):
    r = client.post(
        "/api/auth/register",
        json={"username": "   ", "password": "a", "role": "applicant"},
    )
    assert r.status_code == 400
    assert "username" in r.json()["error"].lower()
