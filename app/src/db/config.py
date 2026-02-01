"""
Database configuration.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)


def get_database_url() -> str:
    """
    Build database URL from environment variables.

    Returns:
        PostgreSQL connection URL
    """
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "whoisalice")
    password = os.getenv("POSTGRES_PASSWORD", "")
    database = os.getenv("POSTGRES_DB", "whoisalice")

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
