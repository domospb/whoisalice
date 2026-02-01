"""
Tests for User domain models.
"""
from uuid import uuid4

from src.domain.user import AdminUser, RegularUser
from src.domain.enums import UserRole


def test_regular_user_creation():
    """Test regular user is created with correct role."""
    user = RegularUser(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == UserRole.REGULAR
    assert user.is_admin() is False


def test_admin_user_creation():
    """Test admin user is created with correct role."""
    user = AdminUser(
        username="admin",
        email="admin@example.com",
        password_hash="hashed_password"
    )
    assert user.role == UserRole.ADMIN
    assert user.is_admin() is True


def test_user_with_wallet():
    """Test user can have wallet reference."""
    wallet_id = uuid4()
    user = RegularUser(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        wallet_id=wallet_id
    )
    assert user.wallet_id == wallet_id
