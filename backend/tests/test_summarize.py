def test_summarize_empty_job_no_key_ok(client):
    """Job with zero applications returns empty summaries without calling OpenAI."""
    hr = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    ).json()
    r = client.post(
        "/api/jobs/5/summarize-resumes",
        headers={"Authorization": f"Bearer {hr['token']}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["summaries"] == []
    assert data.get("top_pick") is None


def test_summarize_requires_openai_key_when_applicants_exist(client, monkeypatch):
    import app.config as app_config
    from pydantic import SecretStr

    monkeypatch.setattr(app_config.settings, "openai_api_key", SecretStr(""))
    hr = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    ).json()
    r = client.post(
        "/api/jobs/1/summarize-resumes",
        headers={"Authorization": f"Bearer {hr['token']}"},
    )
    assert r.status_code == 503
    assert "OPENAI" in r.json()["error"]


def test_summarize_hr_mocked_openai(client, monkeypatch):
    import app.config as app_config
    from pydantic import SecretStr

    # Placeholder only — never a real key; OpenAI is mocked below.
    monkeypatch.setattr(app_config.settings, "openai_api_key", SecretStr("unit-test-mock-not-real"))

    async def fake_summarize(*, api_key, model, job_title, job_description, blocks):
        first_id, first_u, _ = blocks[0]
        return {
            "summaries": [
                {"application_id": bid, "username": un, "summary": f"Summary for {un}"}
                for bid, un, _ in blocks
            ],
            "top_pick": {
                "application_id": first_id,
                "username": first_u,
                "reason": f"Best fit for {job_title}: strongest overlap with role requirements (mock).",
            },
        }

    monkeypatch.setattr("app.main.summarize_top_applicants", fake_summarize)

    hr = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    ).json()
    r = client.post(
        "/api/jobs/1/summarize-resumes",
        headers={"Authorization": f"Bearer {hr['token']}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["summaries"]) == 5
    assert all("Summary for" in s["summary"] for s in data["summaries"])
    assert data["top_pick"] is not None
    assert "reason" in data["top_pick"]
    assert data["top_pick"]["application_id"] in {s["application_id"] for s in data["summaries"]}


def test_summarize_forbidden_for_applicant(client):
    login = client.post(
        "/api/auth/login",
        json={"username": "applicant", "password": "applicant", "role": "applicant"},
    ).json()
    r = client.post(
        "/api/jobs/1/summarize-resumes",
        headers={"Authorization": f"Bearer {login['token']}"},
    )
    assert r.status_code == 403
