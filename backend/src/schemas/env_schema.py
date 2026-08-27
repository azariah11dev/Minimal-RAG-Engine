from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

_env_path = Path(__file__).parent
while not (_env_path / ".env").exists() and _env_path != _env_path.parent:
    _env_path = _env_path.parent

print(f"Loading .env from: {_env_path / '.env'}")  # remove after confirming

class Settings(BaseSettings):
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    DATABASE_URL: Optional[str] = None
    QDRANT_URL: Optional[str] = None

    class Config:
        env_file = str(_env_path / ".env")
        env_file_encoding = "utf-8"

settings = Settings()