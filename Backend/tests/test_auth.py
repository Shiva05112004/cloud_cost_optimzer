from fastapi.testclient import TestClient
from app.main import app
from app.models.database import Base, engine

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def test_register():
    r = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "secret123",
        "full_name": "Test User",
    })
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"


def test_login():
    client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "secret123",
    })
    r = client.post("/api/auth/login", data={
        "username": "login@example.com",
        "password": "secret123",
    })
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_invalid_login():
    r = client.post("/api/auth/login", data={
        "username": "wrong@example.com",
        "password": "wrongpass",
    })
    assert r.status_code == 401