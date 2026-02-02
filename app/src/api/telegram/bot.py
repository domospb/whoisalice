"""
Telegram bot setup and configuration.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from ...core.config import settings
from .handlers import router

logger = logging.getLogger(__name__)

# Global bot and dispatcher instances
bot = None
dp = None


def setup_bot():
    """
    Initialize bot and dispatcher.

    Returns:
        tuple: (Bot, Dispatcher) or (None, None) if token not set
    """
    global bot, dp

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, bot will not start")
        return None, None

    logger.info("Initializing Telegram bot...")

    # Create bot instance
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    # Create dispatcher with memory storage
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register handlers
    dp.include_router(router)

    logger.info("Telegram bot initialized successfully")
    logger.info("Handlers registered")

    return bot, dp


async def start_bot():
    """
    Start bot polling.

    Runs indefinitely until stopped.
    """
    if not bot or not dp:
        logger.error("Bot not initialized. Call setup_bot() first.")
        return

    logger.info("Starting Telegram bot polling...")

    try:
        # Delete webhook if exists (for polling mode)
        await bot.delete_webhook(drop_pending_updates=True)

        # Start polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as e:
        logger.error(f"Bot polling error: {e}")
        raise
    finally:
        await stop_bot()


async def stop_bot():
    """Stop bot and close session."""
    logger.info("Stopping Telegram bot...")

    if bot:
        await bot.session.close()

    logger.info("Telegram bot stopped")


async def main():
    """Main entry point for running the bot."""
    logger.info("=== Starting WhoIsAlice Telegram Bot ===")

    # Setup bot
    setup_bot()

    # Start polling
    await start_bot()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run bot
    asyncio.run(main())
