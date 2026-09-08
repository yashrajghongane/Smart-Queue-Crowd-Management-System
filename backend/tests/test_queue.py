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

    # Create Staff
    s = Staff(username="staff1", password_hash=pwd_context.hash("pass"), display_name="John Doe")
    db.add(s)

    # Create Dept and Room
    d = Department(name="Eye", code="E")
    db.add(d)
    db.commit()
    db.refresh(d)

    r = Room(name_or_number="5", department_id=d.id)
    db.add(r)

    # Create a Token
    p = Patient(full_name="Alice", mobile="000")
    db.add(p)
    db.commit()
    db.refresh(p)

    v = Visit(patient_id=p.id, department_id=d.id)
    db.add(v)
    db.commit()
    db.refresh(v)

    t = Token(visit_id=v.id, department_id=d.id, display_token="E101")
    db.add(t)
    db.commit()

    yield
    Base.metadata.drop_all(bind=engine)

def test_login_and_me():
    res = client.post("/api/auth/login", json={"username": "staff1", "password": "pass"})
    assert res.status_code == 200
    assert "session_id" in res.cookies

    # Test me
    res_me = client.get("/api/auth/me", cookies=res.cookies)
    assert res_me.status_code == 200
    # Only id, display_name and role are returned by /me endpoint, let's check display_name instead
    assert res_me.json()["staff"]["display_name"] == "John Doe"

def test_queue_workflow():
    db = SessionLocal()
    dept = db.query(Department).first()
    db.close()

    login_res = client.post("/api/auth/login", json={"username": "staff1", "password": "pass"})
    cookies = login_res.cookies

    # Call next
    res = client.post(f"/api/staff/queue/{dept.id}/next", cookies=cookies)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SERVING"
    token_id = data["token_id"]

    # Complete
    res = client.post(f"/api/staff/token/{token_id}/complete", cookies=cookies)
    assert res.status_code == 200
    assert res.json()["status"] == "COMPLETED"

    # Try calling next again - should fail (queue empty)
    res = client.post(f"/api/staff/queue/{dept.id}/next", cookies=cookies)
    assert res.status_code == 400
    assert res.json()["detail"]["error"] == "QUEUE_EMPTY"
