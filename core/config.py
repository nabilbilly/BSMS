import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Classhouse Bulk SMS"
    DATABASE_URL: str = "sqlite:///./classhouse.db"
    SECRET_KEY: str = "SUPER_SECRET_KEY_FOR_DEV_ONLY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 1 day

    # Redis for Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Frontend URL for CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # SMS Gateways (Hubtel)
    SMS_API_KEY: str = ""
    SMS_SENDER_ID: str = "ClassHouse"
    HUBTEL_CLIENT_ID: str = ""
    HUBTEL_CLIENT_SECRET: str = ""

    # Email Gateway (Brevo)
    BREVO_API_KEY: str = ""
    BREVO_SENDER_EMAIL: str = "noreply@classhouse.com"
    BREVO_SENDER_NAME: str = "Class House Electronics"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
