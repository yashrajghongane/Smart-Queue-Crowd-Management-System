import pytest
from fastapi.testclient import TestClient
from app.server import app
from app.database import Base, engine, SessionLocal
from app.occupancy_models import Zone, Device
from app.auth_models import pwd_context
from datetime import datetime

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create Zone and Device
    z = Zone(name="Waiting Area A", capacity=30)
    db.add(z)
    db.commit()
    db.refresh(z)

    d = Device(
        device_identifier="ESP32-01",
        device_secret_hash_or_equivalent=pwd_context.hash("supersecret"),
        zone_id=z.id
    )
    db.add(d)
    db.commit()

    yield
    Base.metadata.drop_all(bind=engine)

def test_occupancy_idempotency():
    db = SessionLocal()
    device = db.query(Device).first()
    db.close()

    headers = {"X-Device-Secret": "supersecret"}
    payload = {
        "event_type": "ENTRY",
        "event_id": "evt-001",
        "occurred_at": datetime.utcnow().isoformat() + "Z"
    }

    # First request
    res1 = client.post(f"/api/devices/{device.id}/events", json=payload, headers=headers)
    assert res1.status_code == 200

    # Check count
    res_get = client.get(f"/api/zones/{device.zone_id}/occupancy")
    assert res_get.status_code == 200
    assert res_get.json()["current_count"] == 1

    # Second request (retried, same ID)
    res2 = client.post(f"/api/devices/{device.id}/events", json=payload, headers=headers)
    assert res2.status_code == 200
    assert "already processed" in res2.json()["message"]

    # Check count remains 1
    res_get2 = client.get(f"/api/zones/{device.zone_id}/occupancy")
    assert res_get2.json()["current_count"] == 1

def test_occupancy_floor():
    db = SessionLocal()
    device = db.query(Device).first()
    db.close()

    headers = {"X-Device-Secret": "supersecret"}

    # Issue 2 EXITs with different IDs
    for i in range(2):
        payload = {
            "event_type": "EXIT",
            "event_id": f"evt-exit-{i}",
            "occurred_at": datetime.utcnow().isoformat() + "Z"
        }
        res = client.post(f"/api/devices/{device.id}/events", json=payload, headers=headers)
        assert res.status_code == 200

    # Ensure it doesn't go below 0
    res_get = client.get(f"/api/zones/{device.zone_id}/occupancy")
    assert res_get.json()["current_count"] == 0
