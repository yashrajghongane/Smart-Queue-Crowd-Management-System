import pytest
from fastapi.testclient import TestClient
from app.server import app
from app.database import Base, engine, SessionLocal
from app.models import Department, Room, Patient, Visit, Token

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create Dept and Room
    d = Department(name="Eye", code="E")
    db.add(d)
    db.commit()
    db.refresh(d)

    r = Room(name_or_number="5", department_id=d.id)
    db.add(r)

    # Create Tokens
    p = Patient(full_name="Alice", mobile="000")
    db.add(p)
    db.commit()
    db.refresh(p)

    v = Visit(patient_id=p.id, department_id=d.id)
    db.add(v)
    db.commit()
    db.refresh(v)

    t = Token(visit_id=v.id, department_id=d.id, display_token="E101", status_access_id="secret1")
    db.add(t)
    db.commit()

    yield
    Base.metadata.drop_all(bind=engine)

def test_get_status():
    res = client.get("/api/status/secret1")
    assert res.status_code == 200
    data = res.json()
    assert data["display_token"] == "E101"
    assert data["department"] == "Eye"

def test_get_display():
    db = SessionLocal()
    dept = db.query(Department).filter(Department.name == "Eye").first()
    db.close()

    res = client.get(f"/api/display/{dept.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["department"] == "Eye"
    assert data["next_token"] == "E101"
