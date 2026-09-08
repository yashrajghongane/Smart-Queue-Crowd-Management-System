from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class PatientType(str, enum.Enum):
    NEW = "NEW"
    FOLLOW_UP = "FOLLOW_UP"

class TokenStatus(str, enum.Enum):
    WAITING = "WAITING"
    SERVING = "SERVING"
    HOLD = "HOLD"
    SKIPPED = "SKIPPED"
    COMPLETED = "COMPLETED"

class PriorityType(str, enum.Enum):
    NORMAL = "NORMAL"
    PRIORITY = "PRIORITY"
    EMERGENCY = "EMERGENCY"

class Department(Base):
    __tablename__ = "departments"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

from app.auth_models import Staff, StaffSession, QueueEvent
from app.occupancy_models import Zone, Device, OccupancyEvent, OccupancyState

class Room(Base):
    __tablename__ = "rooms"
    id = Column(String, primary_key=True, default=generate_uuid)
    name_or_number = Column(String, nullable=False)
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RegistrationLocation(Base):
    __tablename__ = "registration_locations"
    id = Column(String, primary_key=True, default=generate_uuid)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    name = Column(String, nullable=False)
    qr_public_id = Column(String, nullable=False, unique=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Patient(Base):
    __tablename__ = "patients"
    id = Column(String, primary_key=True, default=generate_uuid)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(String, nullable=True)
    mobile = Column(String, nullable=False, index=True)
    patient_type_default = Column(String, nullable=True)
    verification_status = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class PatientVerification(Base):
    __tablename__ = "patient_verifications"
    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=True)
    mobile = Column(String, nullable=False)
    method = Column(String, nullable=False)
    challenge_reference = Column(String, nullable=True)
    status = Column(String, nullable=False)
    attempt_count = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Visit(Base):
    __tablename__ = "visits"
    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    status = Column(String, nullable=False, default="WAITING") # Maps to token status conceptually
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Token(Base):
    __tablename__ = "tokens"
    id = Column(String, primary_key=True, default=generate_uuid)
    visit_id = Column(String, ForeignKey("visits.id"), nullable=False, unique=True)
    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    display_token = Column(String, nullable=False)
    status = Column(String, nullable=False, default=TokenStatus.WAITING.value)
    priority = Column(String, nullable=False, default=PriorityType.NORMAL.value)
    room_id = Column(String, ForeignKey("rooms.id"), nullable=True)
    status_access_id = Column(String, nullable=False, unique=True, default=generate_uuid)
    called_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
