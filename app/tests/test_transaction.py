"""
Tests for Transaction domain models.
"""
import pytest

from src.domain.transaction import CreditTransaction, DebitTransaction
from src.domain.wallet import Wallet
from src.domain.user import RegularUser


def test_credit_transaction_apply():
    """Test credit transaction adds balance."""
    wallet = Wallet()
    user = RegularUser("test", "test@example.com", "hash")
    
    transaction = CreditTransaction(
        amount=100.0,
        wallet=wallet,
        user=user
    )
    transaction.apply()
    
    assert wallet.balance == 100.0


def test_debit_transaction_apply():
    """Test debit transaction deducts balance."""
    wallet = Wallet(balance=200.0)
    user = RegularUser("test", "test@example.com", "hash")
    
    transaction = DebitTransaction(
        amount=50.0,
        wallet=wallet,
        user=user
    )
    transaction.apply()
    
    assert wallet.balance == 150.0


def test_debit_transaction_insufficient():
    """Test debit transaction fails with insufficient balance."""
    wallet = Wallet(balance=10.0)
    user = RegularUser("test", "test@example.com", "hash")
    
    transaction = DebitTransaction(
        amount=50.0,
        wallet=wallet,
        user=user
    )
    
    with pytest.raises(ValueError, match="Insufficient balance"):
        transaction.apply()


def test_transaction_invalid_amount():
    """Test transaction with invalid amount raises error."""
    wallet = Wallet()
    user = RegularUser("test", "test@example.com", "hash")
    
    with pytest.raises(ValueError, match="Transaction amount must be positive"):
        CreditTransaction(amount=-10.0, wallet=wallet, user=user)
