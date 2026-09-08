import os
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Department, Room

def seed_data():
    db = SessionLocal()
    try:
        # Check if departments exist
        if db.query(Department).count() == 0:
            deps = [
                {"name": "General Medicine", "code": "G", "room": "2"},
                {"name": "Dental", "code": "D", "room": "4"},
                {"name": "Eye", "code": "E", "room": "5"},
            ]
            for dep_data in deps:
                dept = Department(name=dep_data["name"], code=dep_data["code"])
                db.add(dept)
                db.commit()
                db.refresh(dept)

                room = Room(name_or_number=dep_data["room"], department_id=dept.id)
                db.add(room)
                db.commit()
            print("Seeded departments and rooms successfully.")
        else:
            print("Data already seeded.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
