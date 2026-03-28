import uuid


def test_hr_lists_applicants_includes_demo_pool(client):
    hr = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    ).json()
    tok = hr["token"]
    r1 = client.get("/api/jobs/1/applicants", headers={"Authorization": f"Bearer {tok}"})
    assert r1.status_code == 200
    names = [a["username"] for a in r1.json()["applicants"]]
    assert len(names) == 5
    assert "taylor" in names
    r2 = client.get("/api/jobs/2/applicants", headers={"Authorization": f"Bearer {tok}"})
    assert r2.status_code == 200
    j2 = [a["username"] for a in r2.json()["applicants"]]
    assert len(j2) >= 2
    assert "priya" in j2 or "dev" in j2


def test_applicant_cannot_list_applicants(client):
    login = client.post(
        "/api/auth/login",
        json={"username": "applicant", "password": "applicant", "role": "applicant"},
    ).json()
    r = client.get(
        "/api/jobs/1/applicants",
        headers={"Authorization": f"Bearer {login['token']}"},
    )
    assert r.status_code == 403


def test_applicant_upload_and_hr_download(client):
    login = client.post(
        "/api/auth/login",
        json={"username": "applicant", "password": "applicant", "role": "applicant"},
    ).json()
    tok = login["token"]
    r0 = client.get(
        "/api/jobs/3/my-application",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r0.status_code == 404

    files = {"file": ("my_cv.txt", b"Hello resume content", "text/plain")}
    r_up = client.post(
        "/api/jobs/3/resume",
        headers={"Authorization": f"Bearer {tok}"},
        files=files,
    )
    assert r_up.status_code == 200
    body = r_up.json()
    assert body["original_filename"]
    app_id = body["application_id"]

    r_my = client.get(
        "/api/jobs/3/my-application",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r_my.status_code == 200

    dl_self = client.get(
        f"/api/applications/{app_id}/resume",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert dl_self.status_code == 200
    assert b"Hello resume" in dl_self.content

    hr = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    ).json()
    dl_hr = client.get(
        f"/api/applications/{app_id}/resume",
        headers={"Authorization": f"Bearer {hr['token']}"},
    )
    assert dl_hr.status_code == 200


def test_hr_add_applicant_new_user_then_replace_resume(client):
    hr = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    ).json()
    tok = hr["token"]
    uname = f"hr_seed_{uuid.uuid4().hex[:10]}"
    files = {"file": ("cv.txt", b"First version", "text/plain")}
    r = client.post(
        "/api/jobs/3/hr-applicant-resume",
        headers={"Authorization": f"Bearer {tok}"},
        data={"username": uname},
        files=files,
    )
    assert r.status_code == 200
    j = r.json()
    assert j["created_new_user"] is True
    assert j["username"] == uname
    app_id = j["application_id"]

    files2 = {"file": ("cv2.txt", b"Second version", "text/plain")}
    r2 = client.post(
        "/api/jobs/3/hr-applicant-resume",
        headers={"Authorization": f"Bearer {tok}"},
        data={"username": uname},
        files=files2,
    )
    assert r2.status_code == 200
    j2 = r2.json()
    assert j2["created_new_user"] is False
    assert j2["application_id"] == app_id

    login = client.post(
        "/api/auth/login",
        json={"username": uname, "password": uname, "role": "applicant"},
    ).json()
    dl = client.get(
        f"/api/applications/{app_id}/resume",
        headers={"Authorization": f"Bearer {login['token']}"},
    )
    assert dl.status_code == 200
    assert b"Second version" in dl.content


def test_hr_add_applicant_rejects_existing_hr_username(client):
    hr = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    ).json()
    tok = hr["token"]
    files = {"file": ("cv.txt", b"x", "text/plain")}
    r = client.post(
        "/api/jobs/1/hr-applicant-resume",
        headers={"Authorization": f"Bearer {tok}"},
        data={"username": "hr"},
        files=files,
    )
    assert r.status_code == 400


def test_applicant_cannot_hr_add_resume(client):
    login = client.post(
        "/api/auth/login",
        json={"username": "applicant", "password": "applicant", "role": "applicant"},
    ).json()
    files = {"file": ("cv.txt", b"x", "text/plain")}
    r = client.post(
        "/api/jobs/1/hr-applicant-resume",
        headers={"Authorization": f"Bearer {login['token']}"},
        data={"username": "someone_new"},
        files=files,
    )
    assert r.status_code == 403


def test_list_applicants_respects_limit(client):
    hr = client.post(
        "/api/auth/login",
        json={"username": "hr", "password": "hr", "role": "hr"},
    ).json()
    r = client.get(
        "/api/jobs/1/applicants?limit=2",
        headers={"Authorization": f"Bearer {hr['token']}"},
    )
    assert r.status_code == 200
    assert len(r.json()["applicants"]) <= 2
