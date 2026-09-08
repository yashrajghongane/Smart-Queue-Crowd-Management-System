from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Smart Queue System"

    DATABASE_URL: str = "sqlite:///./queue.db"

    SECRET_KEY: str = "CHANGEME_SECRET_KEY_FOR_TESTING"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    VERIFICATION_PROVIDER: str = "MOCK"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
