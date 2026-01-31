"""
Domain models for the WhoIsAlice ML service.
"""
from .enums import DataType, TaskStatus, TransactionType, UserRole
from .ml_model import MLModel
from .ml_task import MLTask, PredictionResult
from .transaction import CreditTransaction, DebitTransaction, Transaction
from .user import AdminUser, RegularUser, User

__all__ = [
    # Enums
    "UserRole",
    "TaskStatus",
    "TransactionType",
    "DataType",
    # User models
    "User",
    "RegularUser",
    "AdminUser",
    # Transaction models
    "Transaction",
    "CreditTransaction",
    "DebitTransaction",
    # ML models
    "MLModel",
    "MLTask",
    "PredictionResult",
]
