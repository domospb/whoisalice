"""
Balance REST endpoints.

GET /balance - Get current balance
POST /balance/topup - Top-up balance
"""
import logging
from fastapi import APIRouter, Depends, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/balance", tags=["Balance"])

logger.info("Balance router initialized")


@router.get("")
async def get_balance():
    """Get user's current balance."""
    logger.info("GET /balance called")
    # TODO: Implement get balance
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/topup")
async def topup_balance():
    """Top-up user's balance."""
    logger.info("POST /balance/topup called")
    # TODO: Implement balance top-up
    raise HTTPException(status_code=501, detail="Not implemented yet")
