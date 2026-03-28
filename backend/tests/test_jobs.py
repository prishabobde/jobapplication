def test_jobs_requires_auth(client):
    r = client.get("/api/jobs")
    assert r.status_code == 401


def test_jobs_list_after_login(client):
    login = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    ).json()
    r = client.get("/api/jobs", headers={"Authorization": f"Bearer {login['token']}"})
    assert r.status_code == 200
    data = r.json()
    assert "jobs" in data
    titles = {j["title"] for j in data["jobs"]}
    assert titles == {
        "Software Dev",
        "Product Manager",
        "ML Engineer",
        "HR",
        "Financial Analyst",
    }
    for j in data["jobs"]:
        assert j["is_open"] is True
        assert len(j["description"]) > 50


def test_job_detail(client):
    login = client.post(
        "/api/auth/login",
        json={"username": "applicant", "password": "applicant", "role": "applicant"},
    ).json()
    tok = login["token"]
    r = client.get("/api/jobs/1", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
    assert r.json()["title"] == "Software Dev"


def test_job_detail_missing(client):
    login = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    ).json()
    r = client.get("/api/jobs/9999", headers={"Authorization": f"Bearer {login['token']}"})
    assert r.status_code == 404
