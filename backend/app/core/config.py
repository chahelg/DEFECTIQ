"""Application settings for DefectIQ AI."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "DefectIQ AI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "DefectIQ AI MVP"
    SECRET_KEY: str = "local-dev-secret-key-change-in-production-32chars"
    DATABASE_URL: str = "sqlite+aiosqlite:///./defectiq.db"
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DEBUG: bool = True
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    ML_MODELS_DIR: str = "backend/ml/saved_models"
    EMBEDDINGS_MODEL: str = "all-MiniLM-L6-v2"
    MIN_TRAINING_ROWS: int = 20
    ALGORITHM: str = "HS256"
    DOCS_URL: str = "/api/docs"
    REDOC_URL: str = "/api/redoc"
    OPENAPI_URL: str = "/api/openapi.json"
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "").replace("+aiosqlite", "")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

