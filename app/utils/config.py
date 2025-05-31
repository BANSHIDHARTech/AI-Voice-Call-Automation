from pydantic_settings import BaseSettings

import os
from functools import lru_cache

class Settings(BaseSettings):
    # Application settings
    app_name: str = "AI Voice Agent System"
    environment: str = "development"
    debug: bool = True
    
    # Database settings
    db_host: str = "localhost"
    db_name: str = "ai_voice_agent"
    db_username: str = "postgres"
    db_password: str = "postgres"
    
    # API Keys
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    vapi_api_key: str = os.getenv("VAPI_API_KEY", "")
    
    # Feature flags
    use_openai_for_intent: bool = True
    mock_external_services: bool = True  # Set to False in production
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()