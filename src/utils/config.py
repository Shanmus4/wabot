from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # WhatsApp API settings
    WHATSAPP_API_KEY: str = os.getenv("WHATSAPP_API_KEY", "")
    WHATSAPP_API_SECRET: str = os.getenv("WHATSAPP_API_SECRET", "")
    WHATSAPP_PHONE_NUMBER: str = os.getenv("WHATSAPP_PHONE_NUMBER", "")
    
    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    AUTO_DELETE_MESSAGES: bool = os.getenv("AUTO_DELETE_MESSAGES", "True").lower() == "true"
    MESSAGE_RETENTION_HOURS: int = int(os.getenv("MESSAGE_RETENTION_HOURS", "24"))
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 