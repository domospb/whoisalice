"""
Balance request/response schemas.
"""
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BalanceResponse(BaseModel):
    """Balance information response."""

    balance: float
    currency: str


class TopUpRequest(BaseModel):
    """Balance top-up request."""

    amount: float


class TopUpResponse(BaseModel):
    """Balance top-up response."""

    new_balance: float
    currency: str
    transaction_id: str


logger.debug("Balance schemas loaded")
