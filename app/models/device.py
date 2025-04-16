# app/models/device.py
from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid


class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    type = Column(String, index=True)  # "light", "tv", "thermostat"
    room = Column(String, index=True)
    ip_address = Column(String)
    is_active = Column(Boolean, default=True)
    state = Column(JSON, default={})  # Current state as JSON
    config = Column(JSON, default={})  # Device-specific configuration
