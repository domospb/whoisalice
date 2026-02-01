"""
Tests for Wallet domain model.
"""
import pytest

from src.domain.wallet import Wallet


def test_wallet_creation():
    """Test wallet is created with default values."""
    wallet = Wallet()
    assert wallet.balance == 0.0
    assert wallet.currency == "USD"
    assert wallet.id is not None


def test_wallet_add_balance():
    """Test adding balance to wallet."""
    wallet = Wallet()
    wallet.add_balance(100.0)
    assert wallet.balance == 100.0


def test_wallet_add_balance_invalid():
    """Test adding negative balance raises error."""
    wallet = Wallet()
    with pytest.raises(ValueError, match="Amount to add must be positive"):
        wallet.add_balance(-10.0)


def test_wallet_deduct_balance():
    """Test deducting balance from wallet."""
    wallet = Wallet(balance=100.0)
    wallet.deduct_balance(30.0)
    assert wallet.balance == 70.0


def test_wallet_deduct_insufficient():
    """Test deducting more than balance raises error."""
    wallet = Wallet(balance=50.0)
    with pytest.raises(ValueError, match="Insufficient balance"):
        wallet.deduct_balance(100.0)


def test_wallet_can_afford():
    """Test can_afford checks balance correctly."""
    wallet = Wallet(balance=100.0)
    assert wallet.can_afford(50.0) is True
    assert wallet.can_afford(100.0) is True
    assert wallet.can_afford(150.0) is False
