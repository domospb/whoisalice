"""
Telegram bot message handlers.

Commands:
- /start - Welcome message
- /register - Register new user
- /login - Login
- /balance - View balance
- /topup - Top-up balance
- /history - View history

Message handlers:
- Text messages - Text prediction
- Voice messages - Audio prediction
"""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = logging.getLogger(__name__)

router = Router()

logger.info("Telegram handlers initialized")


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    logger.info(f"User {message.from_user.id} started bot")
    # TODO: Send welcome message
    await message.answer("Welcome to WhoIsAlice! (Not implemented yet)")


@router.message(Command("register"))
async def cmd_register(message: Message):
    """Handle /register command."""
    logger.info(f"User {message.from_user.id} - /register")
    # TODO: Start registration flow
    await message.answer("Registration not implemented yet")


@router.message(Command("login"))
async def cmd_login(message: Message):
    """Handle /login command."""
    logger.info(f"User {message.from_user.id} - /login")
    # TODO: Start login flow
    await message.answer("Login not implemented yet")


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    """Handle /balance command."""
    logger.info(f"User {message.from_user.id} - /balance")
    # TODO: Show balance
    await message.answer("Balance check not implemented yet")


@router.message(Command("topup"))
async def cmd_topup(message: Message):
    """Handle /topup command."""
    logger.info(f"User {message.from_user.id} - /topup")
    # TODO: Top-up flow
    await message.answer("Top-up not implemented yet")


@router.message(Command("history"))
async def cmd_history(message: Message):
    """Handle /history command."""
    logger.info(f"User {message.from_user.id} - /history")
    # TODO: Show history
    await message.answer("History not implemented yet")


@router.message()
async def handle_text_message(message: Message):
    """Handle text messages."""
    logger.info(f"User {message.from_user.id} sent text: {message.text[:50]}")
    # TODO: Process text prediction
    await message.answer("Text prediction not implemented yet")


# TODO: Add voice message handler
# TODO: Add audio file handler
