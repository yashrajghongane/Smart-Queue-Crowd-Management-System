from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.sql import func
from app.database import Base
from app.models import generate_uuid

class Zone(Base):
    __tablename__ = "zones"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Device(Base):
    __tablename__ = "devices"
    id = Column(String, primary_key=True, default=generate_uuid)
    device_identifier = Column(String, unique=True, nullable=False)
    device_secret_hash_or_equivalent = Column(String, nullable=False)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=False)
    active = Column(Boolean, default=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class OccupancyEvent(Base):
    __tablename__ = "occupancy_events"
    id = Column(String, primary_key=True, default=generate_uuid)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=False)
    event_id = Column(String, unique=True, nullable=False) # for idempotency
    event_type = Column(String, nullable=False) # ENTRY, EXIT
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OccupancyState(Base):
    __tablename__ = "occupancy_state"
    zone_id = Column(String, ForeignKey("zones.id"), primary_key=True)
    current_count = Column(Integer, default=0, nullable=False)
    capacity = Column(Integer, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
