"""
Telegram bot keyboards and buttons.
"""
import logging
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
)

logger = logging.getLogger(__name__)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    logger.debug("Creating main keyboard")
    # TODO: Implement main menu keyboard
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Not ready")]])


def get_balance_keyboard() -> InlineKeyboardMarkup:
    """Get balance operations keyboard."""
    logger.debug("Creating balance keyboard")
    # TODO: Implement balance keyboard
    return InlineKeyboardMarkup(inline_keyboard=[])


logger.debug("Keyboard utilities loaded")
