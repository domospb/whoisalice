"""
Database initialization utilities.
"""
from sqlalchemy.ext.asyncio import AsyncEngine

from .models import (
    MLModelModel,
    MLTaskModel,
    PredictionResultModel,
    TransactionModel,
    UserModel,
    WalletModel,
)
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


async def drop_tables():
    """
    Drop all database tables.

    WARNING: This deletes all data!
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
