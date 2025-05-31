from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class CallDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class CallStatus(str, enum.Enum):
    QUEUED = "queued"
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"

class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String(255), unique=True, index=True)
    phone_number = Column(String(20), index=True)
    to_number = Column(String(20))
    direction = Column(Enum(CallDirection), index=True)
    status = Column(Enum(CallStatus), default=CallStatus.QUEUED)
    duration = Column(Float, default=0.0)
    language = Column(String(10), default="en")
    transcript = Column(Text, nullable=True)
    intent = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recordings = relationship("Recording", back_populates="call")
    actions = relationship("CallAction", back_populates="call")

class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"))
    recording_sid = Column(String(255), unique=True, index=True, nullable=True)
    recording_url = Column(String(255))
    duration = Column(Float, default=0.0)
    transcript = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    call = relationship("Call", back_populates="recordings")

class ActionType(str, enum.Enum):
    CALLBACK = "callback"
    TICKET = "ticket"
    ESCALATION = "escalation"
    RESOLVED = "resolved"
    OTHER = "other"

class CallAction(Base):
    __tablename__ = "call_actions"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"))
    action_type = Column(Enum(ActionType))
    details = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    call = relationship("Call", back_populates="actions")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"))
    ticket_number = Column(String(50), unique=True, index=True)
    subject = Column(String(255))
    description = Column(Text)
    status = Column(String(50), default="open")
    assigned_to = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())