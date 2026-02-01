"""
Test script for database operations.

Tests all required functionality:
- User creation
- Balance top-up
- Credit deduction
- Transaction history
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.db.repositories.transaction import TransactionRepository
from src.db.repositories.user import UserRepository
from src.db.repositories.wallet import WalletRepository
from src.db.session import AsyncSessionLocal


async def test_operations():
    """Test all business operations."""
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        wallet_repo = WalletRepository(session)
        transaction_repo = TransactionRepository(session)

        print("=" * 60)
        print("Testing Database Operations")
        print("=" * 60)
        print()

        # 1. Get demo user
        print("1. Getting demo user...")
        demo_user = await user_repo.get_by_username("demo_user")
        if demo_user:
            print(f"   ✓ User: {demo_user.username}")
            print(f"   ✓ Email: {demo_user.email}")
            print(f"   ✓ Role: {demo_user.role}")
            print(f"   ✓ Wallet ID: {demo_user.wallet_id}")
            if demo_user.wallet:
                print(f"   ✓ Current balance: ${demo_user.wallet.balance}")
        else:
            print("   ✗ Demo user not found!")
            return
        print()

        # 2. Top-up balance
        print("2. Testing balance top-up (+$50)...")
        wallet = demo_user.wallet
        old_balance = float(wallet.balance)
        new_balance = old_balance + 50.0
        await wallet_repo.update_balance(wallet.id, new_balance)

        # Record transaction
        credit_tx = await transaction_repo.create(
            amount=50.0,
            transaction_type="credit",
            wallet_id=wallet.id,
            user_id=demo_user.id,
            description="Balance top-up",
        )
        print(f"   ✓ Old balance: ${old_balance}")
        print(f"   ✓ New balance: ${new_balance}")
        print(f"   ✓ Transaction recorded: {credit_tx.id}")
        print()

        # 3. Deduct credits (simulating ML prediction cost)
        print("3. Testing credit deduction (-$10 for ML prediction)...")
        old_balance = new_balance
        new_balance = old_balance - 10.0
        await wallet_repo.update_balance(wallet.id, new_balance)

        # Record transaction
        debit_tx = await transaction_repo.create(
            amount=10.0,
            transaction_type="debit",
            wallet_id=wallet.id,
            user_id=demo_user.id,
            description="ML prediction cost",
        )
        print(f"   ✓ Old balance: ${old_balance}")
        print(f"   ✓ New balance: ${new_balance}")
        print(f"   ✓ Transaction recorded: {debit_tx.id}")
        print()

        # 4. Get transaction history
        print("4. Getting transaction history...")
        transactions = await transaction_repo.get_by_wallet(wallet.id)
        print(f"   ✓ Total transactions: {len(transactions)}")
        print()
        for i, tx in enumerate(transactions, 1):
            print(
                f"   [{i}] {tx.transaction_type.upper()}: ${tx.amount} - "
                f"{tx.description}"
            )
            print(f"       Timestamp: {tx.timestamp}")
            print()

        # 5. Get user transaction history
        print("5. Getting user transaction history...")
        user_transactions = await transaction_repo.get_by_user(demo_user.id)
        print(f"   ✓ User has {len(user_transactions)} transactions")
        print()

        # 6. Verify final balance
        print("6. Verifying final balance...")
        updated_user = await user_repo.get_by_id(demo_user.id)
        if updated_user and updated_user.wallet:
            print(f"   ✓ Final balance: ${updated_user.wallet.balance}")
            print(f"   ✓ Expected: ${new_balance}")
            assert float(updated_user.wallet.balance) == new_balance
        print()

        print("=" * 60)
        print("✅ All operations completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_operations())
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Error: {e}")
        print("=" * 60)
        import traceback

        traceback.print_exc()
        sys.exit(1)
