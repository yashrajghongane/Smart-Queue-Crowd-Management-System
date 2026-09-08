import pytest
from fastapi.testclient import TestClient
from app.server import app
from app.database import Base, engine, SessionLocal
from app.models import Department, Room, Patient, Visit, Token
from app.auth_models import Staff, pwd_context

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create Staff (STAFF)
    s1 = Staff(username="staff_only", password_hash=pwd_context.hash("pass"), display_name="John Staff", role="STAFF")
    db.add(s1)

    # Create Admin (ADMIN)
    s2 = Staff(username="admin_user", password_hash=pwd_context.hash("pass"), display_name="Jane Admin", role="ADMIN")
    db.add(s2)

    d = Department(name="Cardio", code="C")
    db.add(d)
    db.commit()
    db.refresh(d)

    p = Patient(full_name="Bob", mobile="111")
    db.add(p)
    db.commit()
    db.refresh(p)

    v = Visit(patient_id=p.id, department_id=d.id)
    db.add(v)
    db.commit()
    db.refresh(v)

    t = Token(visit_id=v.id, department_id=d.id, display_token="C101")
    db.add(t)
    db.commit()

    yield
    Base.metadata.drop_all(bind=engine)

def test_role_enforcement():
    # Login as normal STAFF
    login_staff = client.post("/api/auth/login", json={"username": "staff_only", "password": "pass"})
    cookies_staff = login_staff.cookies

    # Login as ADMIN
    login_admin = client.post("/api/auth/login", json={"username": "admin_user", "password": "pass"})
    cookies_admin = login_admin.cookies

    db = SessionLocal()
    token = db.query(Token).first()
    db.close()

    # Staff attempts to set priority (Requires ADMIN)
    res_staff = client.post(f"/api/staff/token/{token.id}/priority", json={"priority": "EMERGENCY"}, cookies=cookies_staff)
    assert res_staff.status_code == 403
    assert res_staff.json()["detail"]["error"] == "FORBIDDEN"

    # Admin attempts to set priority
    res_admin = client.post(f"/api/staff/token/{token.id}/priority", json={"priority": "EMERGENCY"}, cookies=cookies_admin)
    assert res_admin.status_code == 200
    assert res_admin.json()["priority"] == "EMERGENCY"

def test_invalid_state_transition():
    login_admin = client.post("/api/auth/login", json={"username": "admin_user", "password": "pass"})
    cookies = login_admin.cookies

    db = SessionLocal()
    token = db.query(Token).first()
    db.close()

    # Complete the token
    res = client.post(f"/api/staff/token/{token.id}/complete", cookies=cookies)
    assert res.status_code == 200

    # Try to hold a completed token
    res = client.post(f"/api/staff/token/{token.id}/hold", cookies=cookies)
    assert res.status_code == 400
    assert res.json()["detail"]["error"] == "INVALID_STATE_TRANSITION"
