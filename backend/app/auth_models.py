from passlib.context import CryptContext
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base
from app.models import generate_uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Staff(Base):
    __tablename__ = "staff"
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="STAFF") # ADMIN, STAFF, etc
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

class StaffSession(Base):
    __tablename__ = "staff_sessions"
    id = Column(String, primary_key=True, default=generate_uuid)
    staff_id = Column(String, ForeignKey("staff.id"), nullable=False)
    session_identifier_hash = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

class QueueEvent(Base):
    __tablename__ = "queue_events"
    id = Column(String, primary_key=True, default=generate_uuid)
    token_id = Column(String, ForeignKey("tokens.id"), nullable=False)
    visit_id = Column(String, ForeignKey("visits.id"), nullable=False)
    actor_type = Column(String, nullable=False) # STAFF, SYSTEM, PATIENT
    actor_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    from_status = Column(String, nullable=True)
    to_status = Column(String, nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
