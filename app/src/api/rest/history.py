"""
History REST endpoints.

GET /history/transactions - Get transaction history
GET /history/predictions - Get prediction history
"""
import logging
from fastapi import APIRouter, Depends, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history", tags=["History"])

logger.info("History router initialized")


@router.get("/transactions")
async def get_transactions():
    """Get user's transaction history."""
    logger.info("GET /history/transactions called")
    # TODO: Implement transaction history
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/predictions")
async def get_predictions():
    """Get user's prediction history."""
    logger.info("GET /history/predictions called")
    # TODO: Implement prediction history
    raise HTTPException(status_code=501, detail="Not implemented yet")
