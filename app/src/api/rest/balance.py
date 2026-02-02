"""
Balance REST endpoints.

GET /balance - Get current balance
POST /balance/topup - Top-up balance
"""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_current_user_id
from src.db.session import get_db
from src.services.balance_service import BalanceService
from src.api.schemas.balance import BalanceResponse, TopUpRequest, TopUpResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/balance", tags=["Balance"])

logger.info("Balance router initialized")


@router.get("", response_model=BalanceResponse)
async def get_balance(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Get user's current balance.

    Requires authentication.
    """
    logger.info(f"GET /balance called for user: {user_id}")

    balance_service = BalanceService(session)

    try:
        balance_data = await balance_service.get_balance(UUID(user_id))

        logger.debug(f"Balance retrieved: {balance_data}")

        return BalanceResponse(**balance_data)

    except ValueError as e:
        logger.warning(f"Balance retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Balance retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get balance",
        )


@router.post("/topup", response_model=TopUpResponse)
async def topup_balance(
    request: TopUpRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Top-up user's balance.

    Requires authentication.
    No payment gateway integration (mock top-up).
    """
    logger.info(f"POST /balance/topup called for user {user_id}: ${request.amount}")

    balance_service = BalanceService(session)

    try:
        topup_data = await balance_service.topup_balance(UUID(user_id), request.amount)

        logger.info(f"Balance topped up: {topup_data}")

        return TopUpResponse(**topup_data)

    except ValueError as e:
        logger.warning(f"Top-up failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Top-up error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to top-up balance",
        )
