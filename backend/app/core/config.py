from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./codebuddy.db"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "cb-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    MODEL_PROVIDER: str = "ollama"
    MODEL_NAME: str = "gemma3"
    CORS_ORIGINS: List[str] = ["*"]
    PROJECT_NAME: str = "CODEBUDDY"

    class Config:
        env_file = ".env"

settings = Settings()
