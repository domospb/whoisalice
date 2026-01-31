"""
Enums for the ML service domain model.
"""
from enum import Enum


class UserRole(str, Enum):
    """User role in the system."""
    REGULAR = "regular"
    ADMIN = "admin"


class TaskStatus(str, Enum):
    """Status of ML task execution."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TransactionType(str, Enum):
    """Type of balance transaction."""
    CREDIT = "credit"  # Adding funds to balance
    DEBIT = "debit"    # Deducting funds from balance


class DataType(str, Enum):
    """Type of input/output data for ML tasks."""
    TEXT = "text"      # Text data
    AUDIO = "audio"    # Voice/audio data
