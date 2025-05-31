from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class TwilioWebhookRequest(BaseModel):
    CallSid: str
    CallStatus: str
    From: Optional[str] = None
    To: Optional[str] = None
    RecordingUrl: Optional[str] = None
    RecordingDuration: Optional[int] = None
    TranscriptionText: Optional[str] = None

class VapiWebhookRequest(BaseModel):
    event: str = Field(..., description="Event type (call.started, call.completed, etc.)")
    call_id: str = Field(..., description="Unique identifier for the call")
    direction: str = Field(..., description="Call direction (inbound/outbound)")
    from_number: Optional[str] = Field(None, description="Caller phone number")
    to_number: Optional[str] = Field(None, description="Recipient phone number")
    language: Optional[str] = Field(None, description="Detected language")
    transcript: Optional[str] = Field(None, description="Full call transcript")
    duration: Optional[float] = Field(None, description="Call duration in seconds")
    sentiment: Optional[str] = Field(None, description="Detected sentiment of the call")
    intent: Optional[str] = Field(None, description="Detected intent")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")