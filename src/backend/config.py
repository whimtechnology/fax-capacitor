"""
FaxTriage AI — Configuration Settings
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys - check both variable names
    anthropic_api_key: str = ""

    # Paths
    upload_dir: Path = PROJECT_ROOT / "data" / "uploads"
    database_path: Path = PROJECT_ROOT / "data" / "faxtriage.db"

    # Claude model
    claude_model: str = "claude-sonnet-4-20250514"

    # Upload limits
    max_file_size_mb: int = 50

    # Server settings
    cors_origins: list[str] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Common React dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Check for API key in either variable
        if not self.anthropic_api_key:
            self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "") or \
                                     os.environ.get("ANTHROPIC_CONSOLE_KEY", "")
        # Ensure the anthropic library can find the key
        if self.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = self.anthropic_api_key

    def ensure_directories(self):
        """Create required directories if they don't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
