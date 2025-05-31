from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import enum

class CallStatus(str, enum.Enum):
    QUEUED = "queued"
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"

class CallDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class CallCreate(BaseModel):
    phone_number: str = Field(..., description="Phone number in E.164 format")
    to_number: Optional[str] = Field(None, description="Destination phone number")
    direction: CallDirection
    language: str = Field("en", description="Language code (en/hi)")

class OutboundCallRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number to call in E.164 format")
    message: str = Field(..., description="Message to deliver to the recipient")
    language: str = Field("en", description="Language code (en/hi)")

class InboundCallResponse(BaseModel):
    id: int
    call_sid: str
    status: CallStatus
    message: str = Field("Inbound call received")

class CallResponse(BaseModel):
    id: int
    status: CallStatus
    phone_number: Optional[str] = None
    direction: Optional[CallDirection] = None
    duration: Optional[float] = None
    transcript: Optional[str] = None
    intent: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message: Optional[str] = None
    
    class Config:
        from_attributes = True


class RecordingCreate(BaseModel):
    call_id: int
    recording_sid: Optional[str] = None
    recording_url: str
    duration: Optional[float] = None

class RecordingResponse(BaseModel):
    id: int
    call_id: int
    recording_url: str
    duration: Optional[float] = None
    transcript: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
