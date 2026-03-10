"""Application configuration."""
from pathlib import Path
from pydantic_settings import BaseSettings

# Project root (EquateAI/) when running from backend/
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    app_name: str = "EquateAI - Scientific Equation Platform"
    debug: bool = False

    # API
    api_prefix: str = "/api"

    # Database (relative to cwd unless absolute)
    database_url: str = "sqlite:///./data/equateai.db"

    # File storage (under project root data/)
    upload_dir: Path = _PROJECT_ROOT / "data" / "uploads"
    processed_dir: Path = _PROJECT_ROOT / "data" / "processed"

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_equation_model: str = "qwen2.5:7b"
    ollama_chat_model: str = "qwen2.5:7b"
    ollama_code_model: str = "deepseek-coder:6.7b"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
