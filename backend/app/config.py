from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Auth
    AUTH_AUTO_LINK_FIREBASE_UID: bool = True

    # Application
    APP_NAME: str = "Smart Campus Management System"
    DEBUG: bool = True

    # Redis
    REDIS_URL: Optional[str] = None

    # Email / SMTP
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Firebase Admin SDK (for ID token verification)
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_WEB_API_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_CHECK_REVOKED: bool = True
    # Keep disabled by default because registration creates unverified Firebase users first.
    # Enable in production after adding an email verification flow.
    FIREBASE_REQUIRE_EMAIL_VERIFIED: bool = False

    # AI realtime tuning
    FOOD_RUSH_WS_INTERVAL_SECONDS: int = 8
    AI_STREAM_FRAME_TIMEOUT_SECONDS: int = 120
    AI_STREAM_RETRY_SECONDS: float = 1.5

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
