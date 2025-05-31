from typing import Optional, Dict, Any
import logging
import os
import requests
import json
import base64
from fastapi.responses import Response
import aiohttp
import tempfile
import asyncio

from app.utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class VoiceService:
    def __init__(self):
        self.elevenlabs_api_key = settings.elevenlabs_api_key
        self.openai_api_key = settings.openai_api_key
        self.twilio_account_sid = settings.twilio_account_sid
        self.twilio_auth_token = settings.twilio_auth_token
        self.vapi_api_key = settings.vapi_api_key
        
    async def text_to_speech(self, text: str, language: str = "en") -> bytes:
        """
        Convert text to speech using ElevenLabs API
        
        Args:
            text: The text to convert to speech
            language: The language code (en/hi)
            
        Returns:
            Audio data as bytes
        """
        try:
            # Choose voice based on language
            voice_id = "21m00Tcm4TlvDq8ikWAM" if language == "en" else "AZnzlk1XvdvUeBnXmlld"  # Hindi voice
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            # For demo/mock purposes, we'll return empty bytes
            # In a real implementation, this would make an API call to ElevenLabs
            logger.info(f"Converting text to speech: '{text}' in {language}")
            
            if settings.mock_external_services:
                # Return mock audio data
                return b"MOCK_AUDIO_DATA"
            else:
                # Make actual API call
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            return await response.read()
                        else:
                            error_text = await response.text()
                            logger.error(f"ElevenLabs API error: {error_text}")
                            raise Exception(f"ElevenLabs API error: {response.status}")
                
        except Exception as e:
            logger.error(f"Error in text_to_speech: {e}")
            # Return empty bytes for error case
            return b""
    
    async def transcribe_audio(self, audio_url: str, language: str = "en") -> Optional[str]:
        """
        Transcribe audio using OpenAI Whisper API
        
        Args:
            audio_url: The URL of the audio file to transcribe
            language: The language code (en/hi)
            
        Returns:
            Transcription text or None if failed
        """
        try:
            # For demo/mock purposes, we'll return a dummy transcript
            # In a real implementation, this would download the audio and send to OpenAI
            logger.info(f"Transcribing audio from {audio_url} in {language}")
            
            if settings.mock_external_services:
                # Return mock transcript based on language
                if language == "en":
                    return "I would like to schedule a callback for tomorrow afternoon."
                else:
                    return "मुझे कल दोपहर के लिए एक कॉलबैक शेड्यूल करना होगा।"
            else:
                # Download the audio file
                async with aiohttp.ClientSession() as session:
                    async with session.get(audio_url) as response:
                        if response.status != 200:
                            logger.error(f"Failed to download audio: {response.status}")
                            return None
                        
                        # Save the audio to a temporary file
                        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                            temp_file.write(await response.read())
                            temp_file_path = temp_file.name
                
                # Transcribe with OpenAI Whisper
                try:
                    openai_url = "https://api.openai.com/v1/audio/transcriptions"
                    headers = {
                        "Authorization": f"Bearer {self.openai_api_key}"
                    }
                    
                    with open(temp_file_path, "rb") as audio_file:
                        files = {
                            "file": audio_file,
                            "model": (None, "whisper-1"),
                            "language": (None, language)
                        }
                        
                        async with aiohttp.ClientSession() as session:
                            async with session.post(openai_url, headers=headers, data=files) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    return result.get("text")
                                else:
                                    error_text = await response.text()
                                    logger.error(f"OpenAI API error: {error_text}")
                                    return None
                                
                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                
        except Exception as e:
            logger.error(f"Error in transcribe_audio: {e}")
            return None
    
    def generate_twilio_welcome_twiml(self) -> Response:
        """Generate TwiML for welcoming the caller"""
        twiml = """
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="alice">Welcome to our AI Voice Agent. How can I help you today?</Say>
            <Record maxLength="60" transcribe="true" transcribeCallback="/webhooks/twilio/transcription"/>
        </Response>
        """
        return Response(content=twiml, media_type="application/xml")
    
    def generate_twilio_gather_twiml(self) -> Response:
        """Generate TwiML for gathering speech input"""
        twiml = """
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Gather input="speech" action="/webhooks/twilio/speech" speechTimeout="auto" language="en-US">
                <Say voice="alice">Please tell me how I can help you today.</Say>
            </Gather>
        </Response>
        """
        return Response(content=twiml, media_type="application/xml")
    
    def generate_vapi_assistant_config(self, language: str = "en") -> Dict[str, Any]:
        """Generate Vapi assistant configuration"""
        welcome_message = "Welcome to our AI Voice Agent. How can I help you today?" if language == "en" else "हमारे AI वॉइस एजेंट में आपका स्वागत है। मैं आज आपकी कैसे मदद कर सकता हूँ?"
        
        config = {
            "assistant": {
                "voice": "alloy" if language == "en" else "shimmer",
                "firstMessage": welcome_message,
                "timeoutSettings": {
                    "userResponseTimeout": 10000,
                    "silenceTimeout": 3000
                },
                "endCallSettings": {
                    "endCallThreshold": 0.8
                },
                "language": language,
                "recordCall": True,
                "transcribeCall": True
            },
            "status": "success"
        }
        
        return config