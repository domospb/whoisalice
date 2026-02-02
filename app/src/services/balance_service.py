"""
Balance management service.

Handles:
- View balance
- Top-up balance
- Balance validation
"""
import logging
from uuid import UUID

from src.db.repositories.user import UserRepository
from src.db.repositories.wallet import WalletRepository
from src.db.repositories.transaction import TransactionRepository

logger = logging.getLogger(__name__)


class BalanceService:
    """Balance management service."""

    def __init__(self, session):
        """Initialize with database session."""
        self.session = session
        self.user_repo = UserRepository(session)
        self.wallet_repo = WalletRepository(session)
        self.transaction_repo = TransactionRepository(session)
        logger.info("BalanceService initialized")

    async def get_balance(self, user_id: UUID) -> dict:
        """
        Get user's current balance.

        Args:
            user_id: User UUID

        Returns:
            dict with balance and currency

        Raises:
            ValueError: If user not found
        """
        logger.info(f"Getting balance for user: {user_id}")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise ValueError("User not found")

        if not user.wallet:
            logger.error(f"User {user_id} has no wallet!")
            raise ValueError("User wallet not found")

        balance = float(user.wallet.balance)
        currency = user.wallet.currency

        logger.debug(f"Balance retrieved: {balance} {currency}")

        return {"balance": balance, "currency": currency}

    async def topup_balance(self, user_id: UUID, amount: float) -> dict:
        """
        Top-up user's balance.

        Args:
            user_id: User UUID
            amount: Amount to add

        Returns:
            dict with new_balance, currency, transaction_id

        Raises:
            ValueError: If user not found or amount invalid
        """
        logger.info(f"Topping up balance for user {user_id}: +${amount}")

        if amount <= 0:
            logger.warning(f"Invalid top-up amount: {amount}")
            raise ValueError("Top-up amount must be positive")

        # Get user with wallet
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise ValueError("User not found")

        if not user.wallet:
            logger.error(f"User {user_id} has no wallet!")
            raise ValueError("User wallet not found")

        # Calculate new balance
        old_balance = float(user.wallet.balance)
        new_balance = old_balance + amount

        # Update wallet balance
        logger.debug(f"Updating balance: {old_balance} -> {new_balance}")
        await self.wallet_repo.update_balance(user.wallet.id, new_balance)

        # Create credit transaction
        transaction = await self.transaction_repo.create(
            amount=amount,
            transaction_type="credit",
            description=f"Balance top-up: +${amount}",
            wallet_id=user.wallet.id,
            user_id=user.id,
        )

        logger.info(
            f"Balance topped up: {user_id} | "
            f"{old_balance} -> {new_balance} | TX: {transaction.id}"
        )

        return {
            "new_balance": new_balance,
            "currency": user.wallet.currency,
            "transaction_id": str(transaction.id),
        }

    async def check_sufficient_balance(
        self, user_id: UUID, required_amount: float
    ) -> bool:
        """
        Check if user has sufficient balance.

        Args:
            user_id: User UUID
            required_amount: Amount needed

        Returns:
            True if sufficient balance, False otherwise
        """
        logger.debug(
            f"Checking balance for user {user_id}: required ${required_amount}"
        )

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.wallet:
            logger.warning(f"User or wallet not found: {user_id}")
            return False

        balance = float(user.wallet.balance)
        has_sufficient = balance >= required_amount

        logger.debug(
            f"Balance check: {balance} >= {required_amount} = {has_sufficient}"
        )

        return has_sufficient
