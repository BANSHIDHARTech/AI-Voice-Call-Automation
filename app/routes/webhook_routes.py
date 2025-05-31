from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any

from app.database.db import get_db
from app.services.call_service import CallService
from app.services.voice_service import VoiceService
from app.services.intent_service import IntentService
from app.schemas.webhook import TwilioWebhookRequest, VapiWebhookRequest

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)

@router.post("/twilio")
async def twilio_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook for Twilio call events
    
    This endpoint receives webhook events from Twilio for inbound calls and
    call status updates. It processes these events and updates the call records
    accordingly.
    """
    try:
        form_data = await request.form()
        data = dict(form_data)
        
        call_service = CallService(db)
        voice_service = VoiceService()
        intent_service = IntentService()
        
        # Extract Twilio call SID and event type
        call_sid = data.get("CallSid")
        event_type = data.get("CallStatus")
        
        if not call_sid:
            raise HTTPException(status_code=400, detail="Missing CallSid parameter")
        
        logger.info(f"Received Twilio webhook: {event_type} for call {call_sid}")
        
        if event_type == "initiated" or event_type == "ringing":
            # New inbound call
            phone_number = data.get("From")
            to_number = data.get("To")
            
            # Create a new call record
            call = await call_service.create_inbound_call(
                call_sid=call_sid,
                phone_number=phone_number,
                to_number=to_number
            )
            
            # Prepare TwiML response for the call
            twiml_response = voice_service.generate_twilio_welcome_twiml()
            return twiml_response
            
        elif event_type == "in-progress":
            # Call is in progress, prepare to capture speech
            return voice_service.generate_twilio_gather_twiml()
            
        elif event_type == "completed":
            # Call is completed, process the recording if available
            recording_url = data.get("RecordingUrl")
            
            if recording_url:
                background_tasks.add_task(
                    call_service.process_recording,
                    call_sid=call_sid,
                    recording_url=recording_url
                )
            
            # Update call status
            await call_service.update_call_status(call_sid=call_sid, status="completed")
            
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Error processing Twilio webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vapi")
async def vapi_webhook(
    webhook_data: VapiWebhookRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook for Vapi call events
    
    This endpoint receives webhook events from Vapi for inbound/outbound calls
    and processes them accordingly.
    """
    try:
        call_service = CallService(db)
        voice_service = VoiceService()
        intent_service = IntentService()
        
        event_type = webhook_data.event
        call_id = webhook_data.call_id
        
        logger.info(f"Received Vapi webhook: {event_type} for call {call_id}")
        
        if event_type == "call.started":
            # New call started
            if webhook_data.direction == "inbound":
                # Create a new inbound call record
                call = await call_service.create_inbound_call(
                    call_sid=call_id,
                    phone_number=webhook_data.from_number,
                    to_number=webhook_data.to_number
                )
                
                # Return assistant configuration
                return voice_service.generate_vapi_assistant_config(language=webhook_data.language or "en")
                
        elif event_type == "call.completed":
            # Call is completed
            transcript = webhook_data.transcript
            
            if transcript:
                # Process transcript and extract intent
                intent = await intent_service.extract_intent(transcript)
                
                # Update call record with transcript and intent
                await call_service.update_call_with_transcript(
                    call_sid=call_id,
                    transcript=transcript,
                    intent=intent,
                    duration=webhook_data.duration
                )
                
                # Process any follow-up actions based on intent
                background_tasks.add_task(
                    call_service.process_intent_actions,
                    call_id=call_id,
                    intent=intent
                )
            
            # Update call status
            await call_service.update_call_status(call_sid=call_id, status="completed")
            
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Error processing Vapi webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))