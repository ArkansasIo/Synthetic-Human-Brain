import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_database_url() -> str:
    if os.environ.get("SYNTHETIC_BRAIN_DATABASE_URL"):
        return ""
    try:
        import aiosqlite  # noqa: F401

        return "sqlite+aiosqlite:///./synthetic_brain.db"
    except ImportError:
        return "mysql+asyncmy://synthetic_brain:CHANGE_ME@127.0.0.1:3306/synthetic_brain"


class Settings(BaseSettings):
    app_name: str = "Synthetic Human Brain Research Server"
    version: str = "0.1.0-alpha"
    developer: str = "ArkansasIo"
    database_url: str = Field(default_factory=_default_database_url)
    rust_backend_url: str = "http://127.0.0.1:7800"
    jwt_secret: str = "CHANGE_ME_IN_ENV"
    jwt_algorithm: str = "HS256"
    session_minutes: int = 480
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_prefix="SYNTHETIC_BRAIN_", env_file=".env", extra="ignore")


settings = Settings()
