"""
History REST endpoints.

GET /history/transactions - Get transaction history
GET /history/predictions - Get prediction history
"""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_current_user_id
from src.db.session import get_db
from src.services.history_service import HistoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history", tags=["History"])

logger.info("History router initialized")


@router.get("/transactions")
async def get_transactions(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Get user's transaction history.

    Requires authentication.
    Returns all transactions (credits and debits).
    """
    logger.info(f"GET /history/transactions called for user: {user_id}")

    history_service = HistoryService(session)

    try:
        transactions = await history_service.get_transactions(UUID(user_id))

        logger.info(f"Retrieved {len(transactions)} transactions")

        return {"transactions": transactions}

    except ValueError as e:
        logger.warning(f"Transaction history retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Transaction history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transaction history",
        )


@router.get("/predictions")
async def get_predictions(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Get user's prediction history.

    Requires authentication.
    NOTE: Not fully implemented in Stage 4.
    """
    logger.info(f"GET /history/predictions called for user: {user_id}")

    history_service = HistoryService(session)

    try:
        predictions = await history_service.get_predictions(UUID(user_id))

        logger.info(f"Retrieved {len(predictions)} predictions")

        return {"predictions": predictions}

    except ValueError as e:
        logger.warning(f"Prediction history retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Prediction history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get prediction history",
        )
