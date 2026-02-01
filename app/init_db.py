"""
Database initialization CLI script.

Usage:
    python init_db.py
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.db.seed import init_database


if __name__ == "__main__":
    print("=" * 50)
    print("WhoIsAlice - Database Initialization")
    print("=" * 50)
    print()

    try:
        asyncio.run(init_database())
        print()
        print("=" * 50)
        print("✅ Database initialization successful!")
        print("=" * 50)
    except Exception as e:
        print()
        print("=" * 50)
        print(f"❌ Error: {e}")
        print("=" * 50)
        sys.exit(1)
