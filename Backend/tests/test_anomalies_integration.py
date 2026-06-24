from fastapi.testclient import TestClient
from app.main import app
from app.models.database import Base, engine, SessionLocal
from app.models.account import CloudAccount
from app.models.anomaly_event import AnomalyEvent

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    # drop all to keep tests isolated
    Base.metadata.drop_all(bind=engine)


def test_anomalies_flow_and_authorization():
    # register user A
    r = client.post("/api/auth/register", json={
        "email": "owner@example.com",
        "password": "secret123",
        "full_name": "Owner",
    })
    assert r.status_code == 200

    # login user A
    r = client.post("/api/auth/login", data={"username": "owner@example.com", "password": "secret123"})
    assert r.status_code == 200
    token = r.json().get("access_token")
    assert token

    # create account and anomaly directly via DB
    db = SessionLocal()
    try:
        from app.models.user import User
        user = db.query(User).filter(User.email == 'owner@example.com').first()
        user_id = user.id
    finally:
        pass

    acct = CloudAccount(user_id=user_id, account_name='acct1', role_arn='arn:aws:iam::123:role/demo')
    db.add(acct)
    db.commit()
    db.refresh(acct)

    # create anomaly for this account
    from datetime import date
    evt = AnomalyEvent(account_id=acct.id, cost_date=date.today(), cost_value=100.0)
    db.add(evt)
    db.commit()
    db.refresh(evt)
    anomaly_id = evt.id
    db.close()

    # list anomalies - should include our anomaly
    h = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/anomalies/", headers=h)
    assert r.status_code == 200
    anomalies = r.json().get("anomalies")
    assert any(a["id"] == anomaly_id for a in anomalies)

    # mark false positive as owner - should succeed
    r = client.post(f"/api/anomalies/{anomaly_id}/false-positive", headers=h)
    assert r.status_code == 200
    assert r.json().get('status') in ('recorded', 'recorded')

    # register another user B
    r = client.post("/api/auth/register", json={
        "email": "other@example.com",
        "password": "secret123",
    })
    assert r.status_code == 200
    r = client.post("/api/auth/login", data={"username": "other@example.com", "password": "secret123"})
    token_b = r.json().get("access_token")
    h_b = {"Authorization": f"Bearer {token_b}"}

    # user B should NOT be authorized to refresh or mark false-positive on acct
    r = client.post(f"/api/anomalies/{anomaly_id}/false-positive", headers=h_b)
    assert r.status_code == 403

    r = client.post(f"/api/anomalies/refresh/{acct.id}", headers=h_b)
    assert r.status_code == 403
