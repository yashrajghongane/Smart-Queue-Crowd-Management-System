from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from pydantic import BaseModel, constr
from typing import Optional, List
import uuid

from app.database import get_db
from app.models import Department, Patient, Visit, Token, TokenStatus, Room

router = APIRouter()

class RegisterRequest(BaseModel):
    registration_location_id: str
    name: str
    date_of_birth: Optional[str] = None
    mobile: str
    department_id: str
    patient_type: str
    verification_token: Optional[str] = None
    anti_bot_token: Optional[str] = None

class DepartmentResponse(BaseModel):
    id: str
    name: str
    code: str
    room: Optional[str] = None
    active: bool

class DepartmentsListResponse(BaseModel):
    departments: List[DepartmentResponse]

@router.get("/departments", response_model=DepartmentsListResponse)
def get_departments(db: Session = Depends(get_db)):
    departments = db.query(Department).filter(Department.active == True).all()
    res = []
    for d in departments:
        # get first active room as default for demo purposes
        room = db.query(Room).filter(Room.department_id == d.id, Room.active == True).first()
        res.append(DepartmentResponse(
            id=d.id,
            name=d.name,
            code=d.code,
            room=room.name_or_number if room else None,
            active=d.active
        ))
    return DepartmentsListResponse(departments=res)

@router.post("/register")
def register_patient(req: RegisterRequest, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == req.department_id).first()
    if not dept:
        raise HTTPException(status_code=400, detail={"error": "VALIDATION_ERROR", "message": "Invalid department"})

    # Check for existing patient or create new
    patient = db.query(Patient).filter(Patient.mobile == req.mobile).first()
    if not patient:
        patient = Patient(
            full_name=req.name,
            date_of_birth=req.date_of_birth,
            mobile=req.mobile,
            patient_type_default=req.patient_type
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

    # Check duplicate active visit (WAITING, SERVING, HOLD)
    active_statuses = [TokenStatus.WAITING.value, TokenStatus.SERVING.value, TokenStatus.HOLD.value]

    existing_token = db.query(Token).join(Visit).filter(
        Visit.patient_id == patient.id,
        Visit.department_id == req.department_id,
        Token.status.in_(active_statuses)
    ).first()

    if existing_token:
        # Return existing active visit state, preventing duplicate
        room = db.query(Room).filter(Room.id == existing_token.room_id).first() if existing_token.room_id else None
        # Must return specific structure for active visit exists
        raise HTTPException(status_code=400, detail={
            "error": "ACTIVE_VISIT_EXISTS",
            "message": "Patient already has an active visit for this department.",
            "visit_id": existing_token.visit_id,
            "display_token": existing_token.display_token,
            "status": existing_token.status,
            "status_url": f"/status/{existing_token.status_access_id}",
            "department": dept.name,
            "room": room.name_or_number if room else None
        })

    # Create new visit and token atomically
    visit = Visit(patient_id=patient.id, department_id=req.department_id)
    db.add(visit)
    db.commit()
    db.refresh(visit)

    # Transaction safe token generation using with_for_update (if supported by DB) or an explicit lock on dept record
    # For SQLite, it locks the whole DB on write, but for Postgres this is a row-level lock.
    locked_dept = db.query(Department).filter(Department.id == req.department_id).with_for_update().first()

    count = db.query(Token).filter(Token.department_id == req.department_id).count()
    display_token = f"{locked_dept.code}{count + 101}"

    room = db.query(Room).filter(Room.department_id == req.department_id, Room.active == True).first()

    status_id = str(uuid.uuid4())
    token = Token(
        visit_id=visit.id,
        department_id=req.department_id,
        display_token=display_token,
        status=TokenStatus.WAITING.value,
        room_id=room.id if room else None,
        status_access_id=status_id
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    return {
        "visit_id": visit.id,
        "token_id": token.id,
        "display_token": token.display_token,
        "department": dept.name,
        "room": room.name_or_number if room else None,
        "status": token.status,
        "status_url": f"/status/{token.status_access_id}"
    }