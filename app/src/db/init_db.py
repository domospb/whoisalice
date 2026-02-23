"""
Database initialization utilities.
"""
from sqlalchemy import text

# Import models to register them with SQLAlchemy metadata
from . import models  # noqa: F401
from .session import Base, engine


async def create_tables():
    """
    Create all database tables.

    This function is idempotent - safe to run multiple times.
    """
    async with engine.begin() as conn:
        # Drop all tables (for development only, remove in production)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    # Add columns for Telegram notifications (idempotent for existing DBs)
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "ALTER TABLE ml_tasks ADD COLUMN IF NOT EXISTS telegram_chat_id BIGINT"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE ml_tasks ADD COLUMN IF NOT EXISTS notified_at TIMESTAMP WITHOUT TIME ZONE"
            )
        )


async def run_telegram_notification_migration() -> None:
    """
    Add telegram_chat_id and notified_at columns to ml_tasks if missing.
    Safe to run on every startup (ADD COLUMN IF NOT EXISTS).
    """
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "ALTER TABLE ml_tasks ADD COLUMN IF NOT EXISTS telegram_chat_id BIGINT"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE ml_tasks ADD COLUMN IF NOT EXISTS notified_at "
                "TIMESTAMP WITHOUT TIME ZONE"
            )
        )


async def drop_tables():
    """
    Drop all database tables.

    WARNING: This deletes all data!
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
