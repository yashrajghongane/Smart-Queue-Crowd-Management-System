import pytest
from fastapi.testclient import TestClient
from app.server import app
from app.database import Base, engine, SessionLocal
from app.models import Department, Room

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Seed data
    if db.query(Department).count() == 0:
        d1 = Department(name="General Medicine", code="G")
        db.add(d1)
        db.commit()
        db.refresh(d1)
        r1 = Room(name_or_number="2", department_id=d1.id)
        db.add(r1)
        db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200

def test_get_departments():
    res = client.get("/api/departments")
    assert res.status_code == 200
    data = res.json()
    assert "departments" in data
    assert len(data["departments"]) > 0

def test_register_patient_and_duplicate():
    db = SessionLocal()
    dept = db.query(Department).first()
    db.close()

    payload = {
        "registration_location_id": "loc_123",
        "name": "Test Patient",
        "mobile": "1234567890",
        "department_id": dept.id,
        "patient_type": "NEW"
    }

    res1 = client.post("/api/register", json=payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert "token_id" in data1
    assert "display_token" in data1

    # Second time should fail with duplicate active visit
    res2 = client.post("/api/register", json=payload)
    assert res2.status_code == 400
    data2 = res2.json()
    assert data2["detail"]["error"] == "ACTIVE_VISIT_EXISTS"
    assert data2["detail"]["display_token"] == data1["display_token"]