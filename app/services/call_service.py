from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import logging
import uuid
import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.models.database import Call, Recording, CallAction, Ticket, CallDirection, CallStatus, ActionType
from app.services.voice_service import VoiceService
from app.services.intent_service import IntentService

logger = logging.getLogger(__name__)

class CallService:
    def __init__(self, db: Session):
        self.db = db
        self.voice_service = VoiceService()
        self.intent_service = IntentService()
    
    async def create_outbound_call(self, phone_number: str, message: str, language: str = "en") -> Call:
        """Create a new outbound call record"""
        call_sid = f"out_{uuid.uuid4().hex}"
        call = Call(
            call_sid=call_sid,
            phone_number=phone_number,
            direction=CallDirection.OUTBOUND,
            status=CallStatus.QUEUED,
            language=language
        )
        self.db.add(call)
        self.db.commit()
        self.db.refresh(call)
        
        logger.info(f"Created outbound call to {phone_number} with ID {call.id}")
        return call
    
    async def create_inbound_call(self, call_sid: str, phone_number: str, to_number: str) -> Call:
        """Create a new inbound call record"""
        call = Call(
            call_sid=call_sid,
            phone_number=phone_number,
            to_number=to_number,
            direction=CallDirection.INBOUND,
            status=CallStatus.INITIATED
        )
        self.db.add(call)
        self.db.commit()
        self.db.refresh(call)
        
        logger.info(f"Created inbound call from {phone_number} with ID {call.id}")
        return call
    
    async def get_call(self, call_id: int) -> Optional[Call]:
        """Get call by ID"""
        return self.db.query(Call).filter(Call.id == call_id).first()
    
    async def get_call_by_sid(self, call_sid: str) -> Optional[Call]:
        """Get call by SID"""
        return self.db.query(Call).filter(Call.call_sid == call_sid).first()
    
    async def update_call_status(self, call_sid: str, status: str) -> Optional[Call]:
        """Update call status"""
        call = await self.get_call_by_sid(call_sid)
        if call:
            call.status = status
            call.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(call)
            logger.info(f"Updated call {call_sid} status to {status}")
        return call
    
    async def update_call_with_transcript(self, call_sid: str, transcript: str, intent: str, duration: float) -> Optional[Call]:
        """Update call with transcript and intent"""
        call = await self.get_call_by_sid(call_sid)
        if call:
            call.transcript = transcript
            call.intent = intent
            call.duration = duration
            call.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(call)
            logger.info(f"Updated call {call_sid} with transcript and intent: {intent}")
        return call
    
    async def list_calls(self, skip: int = 0, limit: int = 100, direction: Optional[str] = None, status: Optional[str] = None) -> List[Call]:
        """List calls with optional filtering"""
        query = self.db.query(Call)
        
        if direction:
            query = query.filter(Call.direction == direction)
        
        if status:
            query = query.filter(Call.status == status)
        
        return query.order_by(desc(Call.created_at)).offset(skip).limit(limit).all()
    
    async def process_recording(self, call_sid: str, recording_url: str) -> None:
        """Process a call recording"""
        try:
            call = await self.get_call_by_sid(call_sid)
            if not call:
                logger.error(f"Call {call_sid} not found")
                return
            
            # Download recording
            logger.info(f"Downloading recording from {recording_url}")
            
            # Create recording record
            recording = Recording(
                call_id=call.id,
                recording_url=recording_url
            )
            self.db.add(recording)
            self.db.commit()
            
            # Transcribe recording
            transcript = await self.voice_service.transcribe_audio(recording_url, call.language)
            if transcript:
                recording.transcript = transcript
                self.db.commit()
                
                # Extract intent
                intent = await self.intent_service.extract_intent(transcript)
                
                # Update call with transcript and intent
                await self.update_call_with_transcript(
                    call_sid=call_sid,
                    transcript=transcript,
                    intent=intent,
                    duration=recording.duration or 0
                )
                
                # Process intent actions
                await self.process_intent_actions(call.id, intent)
                
        except Exception as e:
            logger.error(f"Error processing recording: {e}")
    
    async def process_outbound_call(self, call_id: int, phone_number: str, message: str, language: str = "en") -> None:
        """Process an outbound call"""
        try:
            # Get the call record
            call = self.db.query(Call).filter(Call.id == call_id).first()
            if not call:
                logger.error(f"Call {call_id} not found")
                return
            
            # Update call status
            call.status = CallStatus.INITIATED
            self.db.commit()
            
            # Initialize voice service for TTS
            logger.info(f"Initiating outbound call to {phone_number}")
            
            # In a real implementation, this would integrate with Twilio/Vapi
            # Here we'll simulate the call for demo purposes
            try:
                # Simulate call success
                call.status = CallStatus.IN_PROGRESS
                self.db.commit()
                
                # Convert message to speech
                audio_data = await self.voice_service.text_to_speech(message, language)
                
                # Simulate receiving a response
                simulated_response = "I would like to schedule a callback for tomorrow."
                transcript = simulated_response
                
                # Extract intent from response
                intent = await self.intent_service.extract_intent(transcript)
                
                # Update call with transcript and intent
                call.transcript = transcript
                call.intent = intent
                call.status = CallStatus.COMPLETED
                call.duration = 60.0  # Simulated 60-second call
                call.updated_at = datetime.now()
                self.db.commit()
                
                # Process intent actions
                await self.process_intent_actions(call.id, intent)
                
                logger.info(f"Completed outbound call to {phone_number} with intent: {intent}")
                
            except Exception as e:
                # Handle failure
                call.status = CallStatus.FAILED
                self.db.commit()
                logger.error(f"Failed to complete outbound call: {e}")
                
        except Exception as e:
            logger.error(f"Error processing outbound call: {e}")
    
    async def process_intent_actions(self, call_id: int, intent: str) -> None:
        """Process actions based on detected intent"""
        try:
            # Get the call record
            call = self.db.query(Call).filter(Call.id == call_id).first()
            if not call:
                logger.error(f"Call {call_id} not found")
                return
            
            # Process different intents
            if "schedule" in intent.lower() and "callback" in intent.lower():
                # Schedule a callback
                action = CallAction(
                    call_id=call.id,
                    action_type=ActionType.CALLBACK,
                    details=f"Callback scheduled from intent: {intent}",
                    status="pending"
                )
                self.db.add(action)
                
            elif "ticket" in intent.lower() or "issue" in intent.lower():
                # Create a support ticket
                ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
                ticket = Ticket(
                    call_id=call.id,
                    ticket_number=ticket_number,
                    subject=f"Issue from call {call.phone_number}",
                    description=f"Ticket created from call transcript: {call.transcript}",
                    status="open"
                )
                self.db.add(ticket)
                
                action = CallAction(
                    call_id=call.id,
                    action_type=ActionType.TICKET,
                    details=f"Ticket created: {ticket_number}",
                    status="completed"
                )
                self.db.add(action)
                
            elif "escalate" in intent.lower() or "supervisor" in intent.lower() or "manager" in intent.lower():
                # Escalate to agent
                action = CallAction(
                    call_id=call.id,
                    action_type=ActionType.ESCALATION,
                    details=f"Call escalated to human agent from intent: {intent}",
                    status="pending"
                )
                self.db.add(action)
                
            elif "resolve" in intent.lower() or "solved" in intent.lower() or "fixed" in intent.lower():
                # Mark as resolved
                action = CallAction(
                    call_id=call.id,
                    action_type=ActionType.RESOLVED,
                    details=f"Issue resolved from intent: {intent}",
                    status="completed"
                )
                self.db.add(action)
                
            else:
                # Default action for other intents
                action = CallAction(
                    call_id=call.id,
                    action_type=ActionType.OTHER,
                    details=f"Unclassified intent: {intent}",
                    status="pending"
                )
                self.db.add(action)
            
            self.db.commit()
            logger.info(f"Processed intent '{intent}' for call {call_id}")
            
        except Exception as e:
            logger.error(f"Error processing intent actions: {e}")
    
    async def simulate_inbound_call(self, phone_number: str, message: str, language: str = "en") -> Dict[str, Any]:
        """Simulate an inbound call for testing purposes"""
        try:
            # Create a simulated call SID
            call_sid = f"sim_{uuid.uuid4().hex}"
            
            # Create call record
            call = await self.create_inbound_call(
                call_sid=call_sid,
                phone_number=phone_number,
                to_number="+15551234567"  # Simulated destination number
            )
            
            # Update status to in progress
            call.status = CallStatus.IN_PROGRESS
            call.language = language
            self.db.commit()
            
            # Process the simulated message
            transcript = message
            
            # Extract intent
            intent = await self.intent_service.extract_intent(transcript)
            
            # Update call with transcript and intent
            call.transcript = transcript
            call.intent = intent
            call.status = CallStatus.COMPLETED
            call.duration = 30.0  # Simulated 30-second call
            call.updated_at = datetime.now()
            self.db.commit()
            
            # Process intent actions
            await self.process_intent_actions(call.id, intent)
            
            # Return simulation results
            return {
                "call_id": call.id,
                "call_sid": call_sid,
                "status": "completed",
                "transcript": transcript,
                "intent": intent,
                "actions": [action.action_type for action in call.actions]
            }
            
        except Exception as e:
            logger.error(f"Error simulating inbound call: {e}")
            return {"error": str(e)}