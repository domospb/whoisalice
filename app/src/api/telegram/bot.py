"""
Telegram bot setup and configuration.
"""
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from ...core.config import settings

logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = None
dp = None


def setup_bot():
    """Initialize bot and dispatcher."""
    global bot, dp

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, bot will not start")
        return None, None

    logger.info("Initializing Telegram bot...")
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    logger.info("Telegram bot initialized successfully")
    return bot, dp


async def start_bot():
    """Start bot polling."""
    logger.info("Starting Telegram bot polling...")
    # TODO: Register handlers
    # TODO: Start polling
    logger.info("Telegram bot started")


async def stop_bot():
    """Stop bot."""
    logger.info("Stopping Telegram bot...")
    if bot:
        await bot.session.close()
    logger.info("Telegram bot stopped")
