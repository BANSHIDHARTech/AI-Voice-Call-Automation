from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "sqlite:///./voice_assistant.db"
    openai_api_key: str = ""
    elevenlabs_api_key: str = ""
    deepgram_api_key: str = ""
    default_voice_id: str = "default"
    default_language: str = "en"
    default_voice_model: str = "default"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
