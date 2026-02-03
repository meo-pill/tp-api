from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_login_fail():
    r = client.post("/auth/login", json={
        "username": "wrong",
        "password": "wrong"
    })
    assert r.status_code == 401

