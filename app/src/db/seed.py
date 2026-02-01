"""
Database seeding with demo data.

This script is idempotent - safe to run multiple times.
"""
import asyncio

from .init_db import create_tables
from .repositories.ml_model import MLModelRepository
from .repositories.user import UserRepository
from .repositories.wallet import WalletRepository
from .session import AsyncSessionLocal


async def seed_demo_data():
    """
    Seed database with demo data.

    Creates:
    - Demo user with wallet and initial balance
    - Demo admin with wallet
    - Basic ML models (TTS and STT)

    Idempotent: checks if data exists before creating.
    """
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        wallet_repo = WalletRepository(session)
        model_repo = MLModelRepository(session)

        # Check if demo user already exists
        existing_user = await user_repo.get_by_username("demo_user")
        if not existing_user:
            print("Creating demo user...")
            # Create wallet for demo user
            demo_wallet = await wallet_repo.create(balance=100.0, currency="USD")
            # Create demo user
            demo_user = await user_repo.create(
                username="demo_user",
                email="demo@whoisalice.com",
                password_hash="hashed_demo_password",
                role="regular",
                wallet_id=demo_wallet.id,
            )
            print(f"✓ Demo user created: {demo_user.username} (balance: $100)")
        else:
            print(f"✓ Demo user already exists: {existing_user.username}")

        # Check if demo admin already exists
        existing_admin = await user_repo.get_by_username("admin")
        if not existing_admin:
            print("Creating demo admin...")
            # Create wallet for admin
            admin_wallet = await wallet_repo.create(balance=1000.0, currency="USD")
            # Create admin user
            admin_user = await user_repo.create(
                username="admin",
                email="admin@whoisalice.com",
                password_hash="hashed_admin_password",
                role="admin",
                wallet_id=admin_wallet.id,
            )
            print(f"✓ Demo admin created: {admin_user.username} (balance: $1000)")
        else:
            print(f"✓ Demo admin already exists: {existing_admin.username}")

        # Create ML models if they don't exist
        ml_models_data = [
            {
                "name": "Whisper STT",
                "description": "Speech-to-Text using OpenAI Whisper model",
                "cost_per_prediction": 0.50,
                "version": "1.0.0",
            },
            {
                "name": "GPT-4 TTS",
                "description": "Text-to-Speech using GPT-4 voice synthesis",
                "cost_per_prediction": 1.00,
                "version": "1.0.0",
            },
            {
                "name": "Claude STT",
                "description": "Speech-to-Text using Claude model",
                "cost_per_prediction": 0.75,
                "version": "1.0.0",
            },
            {
                "name": "ElevenLabs TTS",
                "description": "Text-to-Speech using ElevenLabs API",
                "cost_per_prediction": 1.50,
                "version": "1.0.0",
            },
        ]

        for model_data in ml_models_data:
            existing_model = await model_repo.get_by_name(model_data["name"])
            if not existing_model:
                print(f"Creating ML model: {model_data['name']}...")
                model = await model_repo.create(**model_data)
                print(
                    f"✓ ML model created: {model.name} "
                    f"(cost: ${model.cost_per_prediction})"
                )
            else:
                print(f"✓ ML model already exists: {existing_model.name}")

        print("\n✅ Database seeding completed!")


async def init_database():
    """
    Initialize database: create tables and seed demo data.

    This is the main entry point for database setup.
    """
    print("Creating database tables...")
    await create_tables()
    print("✓ Tables created\n")

    print("Seeding demo data...")
    await seed_demo_data()


if __name__ == "__main__":
    # Run initialization
    asyncio.run(init_database())
