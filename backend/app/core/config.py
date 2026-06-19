from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ==========================================
    # API Configuration
    # ==========================================
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Financial Analytics Dashboard"

    # ==========================================
    # CORS
    # ==========================================
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    # ==========================================
    # Database
    # ==========================================
    DATABASE_URL: str

    # ==========================================
    # Redis
    # ==========================================
    REDIS_URL: str = "redis://localhost:6379"

    # ==========================================
    # Alpha Vantage
    # ==========================================
    ALPHA_VANTAGE_API_KEY: Optional[str] = None

    # ==========================================
    # OpenAI
    # ==========================================
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"

    # ==========================================
    # JWT
    # ==========================================
    SECRET_KEY: str = (
        "your-secret-key-here-change-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = (
        60 * 24 * 7
    )

    # ==========================================
    # WebSocket
    # ==========================================
    WS_MESSAGE_QUEUE_SIZE: int = 100

    # ==========================================
    # Scheduler
    # ==========================================
    SCHEDULER_TIMEZONE: str = "UTC"

    # ==========================================
    # Async Database URL
    # ==========================================
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return self.DATABASE_URL.replace(
            "postgresql://",
            "postgresql+asyncpg://"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()