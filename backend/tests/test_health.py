def test_health_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True, "service": "prisha-portal-api"}


def test_root_ok(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"ok": True, "service": "prisha-portal-api"}
