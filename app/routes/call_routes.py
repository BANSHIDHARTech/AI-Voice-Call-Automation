'''from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.database.db import get_db
from app.schemas.call import (
    CallCreate, CallResponse, OutboundCallRequest, 
    InboundCallResponse, CallStatus
)
from app.services.call_service import CallService
from app.services.voice_service import VoiceService
from app.services.intent_service import IntentService
from app.models.call import Call  # assuming you have a Call model

router = APIRouter(prefix="/calls", tags=["Calls"])
logger = logging.getLogger(__name__)


@router.post("/outbound", response_model=CallResponse)
async def create_outbound_call(
    call_request: OutboundCallRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        call_service = CallService(db)
        voice_service = VoiceService()
        
        call = await call_service.create_outbound_call(
            phone_number=call_request.phone_number,
            message=call_request.message,
            language=call_request.language
        )
        
        background_tasks.add_task(
            call_service.process_outbound_call,
            call_id=call.id,
            phone_number=call_request.phone_number,
            message=call_request.message,
            language=call_request.language
        )
        
        return CallResponse(
            id=call.id,
            status=CallStatus.QUEUED,
            message="Outbound call has been queued"
        )
    except Exception as e:
        logger.error(f"Error creating outbound call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{call_id}", response_model=CallResponse)
async def get_call_details(
    call_id: int = Path(..., description="The ID of the call to retrieve"),
    db: Session = Depends(get_db)
):
    try:
        call_service = CallService(db)
        call = await call_service.get_call(call_id)
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return CallResponse(
            id=call.id,
            status=call.status,
            phone_number=call.phone_number,
            direction=call.direction,
            duration=call.duration,
            transcript=call.transcript,
            intent=call.intent,
            created_at=call.created_at,
            updated_at=call.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving call details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[CallResponse])
async def list_calls(
    skip: int = Query(0),
    limit: int = Query(100),
    direction: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        call_service = CallService(db)
        calls = await call_service.list_calls(skip=skip, limit=limit, direction=direction, status=status)
        
        return [
            CallResponse(
                id=call.id,
                status=call.status,
                phone_number=call.phone_number,
                direction=call.direction,
                duration=call.duration,
                transcript=call.transcript,
                intent=call.intent,
                created_at=call.created_at,
                updated_at=call.updated_at
            ) for call in calls
        ]
    except Exception as e:
        logger.error(f"Error listing calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 🔥 New: Get logs for frontend
@router.get("/frontend/call-logs", tags=["Frontend"])
async def get_call_logs_for_frontend(db: Session = Depends(get_db)):
    try:
        call_service = CallService(db)
        calls = await call_service.list_calls(limit=50)
        return [
            {
                "caller_number": call.phone_number,
                "timestamp": call.created_at.isoformat(),
                "intent": call.intent,
                "transcript": call.transcript,
            } for call in calls
        ]
    except Exception as e:
        logger.error(f"Error fetching frontend call logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")


# 🔥 New: Simulate call for frontend demo
@router.post("/frontend/simulate-call", tags=["Frontend"])
async def simulate_frontend_call(db: Session = Depends(get_db)):
    try:
        call_service = CallService(db)
        fake_call = Call(
            phone_number="+91-9876543210",
            direction="outbound",
            status=CallStatus.COMPLETED,
            transcript="Hi, I need to reschedule my appointment.",
            intent="Reschedule Appointment",
            duration=30,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(fake_call)
        db.commit()
        db.refresh(fake_call)
        return {"message": "Fake call log created"}
    except Exception as e:
        logger.error(f"Error simulating frontend call: {e}")
        raise HTTPException(status_code=500, detail="Simulation failed")'''
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database.db import get_db
from app.schemas.call import (
    CallCreate, CallResponse, OutboundCallRequest, 
    InboundCallResponse, CallStatus
)
from app.services.call_service import CallService
from app.services.voice_service import VoiceService
from app.services.intent_service import IntentService

router = APIRouter(prefix="/calls", tags=["Calls"])
logger = logging.getLogger(__name__)

@router.post("/outbound", response_model=CallResponse)
async def create_outbound_call(
    call_request: OutboundCallRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Initiate an outbound call
    
    This endpoint triggers an outbound call to the specified phone number.
    The call will use text-to-speech to deliver the provided message and
    will capture the recipient's response.
    """
    try:
        call_service = CallService(db)
        voice_service = VoiceService()
        
        # Create call record in database
        call = await call_service.create_outbound_call(
            phone_number=call_request.phone_number,
            message=call_request.message,
            language=call_request.language
        )
        
        # Add outbound call task to background tasks
        background_tasks.add_task(
            call_service.process_outbound_call,
            call_id=call.id,
            phone_number=call_request.phone_number,
            message=call_request.message,
            language=call_request.language
        )
        
        return CallResponse(
            id=call.id,
            status=CallStatus.QUEUED,
            message="Outbound call has been queued"
        )
    except Exception as e:
        logger.error(f"Error creating outbound call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{call_id}", response_model=CallResponse)
async def get_call_details(
    call_id: int = Path(..., description="The ID of the call to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get details for a specific call
    """
    try:
        call_service = CallService(db)
        call = await call_service.get_call(call_id)
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return CallResponse(
            id=call.id,
            status=call.status,
            phone_number=call.phone_number,
            direction=call.direction,
            duration=call.duration,
            transcript=call.transcript,
            intent=call.intent,
            created_at=call.created_at,
            updated_at=call.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving call details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[CallResponse])
async def list_calls(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    direction: Optional[str] = Query(None, description="Filter by call direction (inbound/outbound)"),
    status: Optional[str] = Query(None, description="Filter by call status"),
    db: Session = Depends(get_db)
):
    """
    List all calls with optional filtering
    """
    try:
        call_service = CallService(db)
        calls = await call_service.list_calls(skip=skip, limit=limit, direction=direction, status=status)
        
        return [
            CallResponse(
                id=call.id,
                status=call.status,
                phone_number=call.phone_number,
                direction=call.direction,
                duration=call.duration,
                transcript=call.transcript,
                intent=call.intent,
                created_at=call.created_at,
                updated_at=call.updated_at
            ) for call in calls
        ]
    except Exception as e:
        logger.error(f"Error listing calls: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 
