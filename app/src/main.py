"""
WhoIsAlice FastAPI Application.

AI Voice Assistant API with TTS and STT operations.

Stage 5: Integrated with RabbitMQ for asynchronous ML task processing.
"""
import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.rest import auth, balance, predict, history
from .api.telegram.bot import setup_bot, start_bot
from .core.config import settings
from .queue.connection import get_rabbitmq_connection
from .queue.publisher import TaskPublisher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(balance.router, prefix=settings.API_V1_PREFIX)
app.include_router(predict.router, prefix=settings.API_V1_PREFIX)
app.include_router(history.router, prefix=settings.API_V1_PREFIX)

logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} initialized")
logger.info(f"API prefix: {settings.API_V1_PREFIX}")
logger.info("Routers registered: auth, balance, predict, history")


@app.get("/")
async def root():
    """Root endpoint - service information."""
    logger.debug("Root endpoint called")
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.debug("Health check called")
    return {"status": "healthy", "version": settings.VERSION}


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info("API documentation available at /docs")

    # Initialize RabbitMQ connection and publisher
    try:
        logger.info("Initializing RabbitMQ connection...")
        rabbitmq_connection = await get_rabbitmq_connection()
        await rabbitmq_connection.connect()
        channel = await rabbitmq_connection.get_channel()

        # Create task publisher
        task_publisher = TaskPublisher(channel)
        await task_publisher.setup_queue()

        # Store in app state for access in endpoints
        app.state.rabbitmq_connection = rabbitmq_connection
        app.state.task_publisher = task_publisher

        logger.info("RabbitMQ connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        logger.warning("Application will run without queue functionality")
        app.state.rabbitmq_connection = None
        app.state.task_publisher = None

    # Start Telegram bot in background
    try:
        logger.info("Starting Telegram bot...")
        bot_instance, dp_instance = setup_bot()
        if bot_instance and dp_instance:
            # Pass task_publisher to bot for handlers
            if app.state.task_publisher:
                bot_instance.task_publisher = app.state.task_publisher
                logger.info("Task publisher attached to Telegram bot")

            # Run bot in background task
            asyncio.create_task(start_bot())
            logger.info("Telegram bot started successfully")
        else:
            logger.warning("Telegram bot not started (token not configured)")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")
        logger.warning("Application will run without Telegram bot")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"Shutting down {settings.PROJECT_NAME}")

    # Close Telegram bot
    try:
        from .api.telegram.bot import bot

        if bot:
            await bot.session.close()
            logger.info("Telegram bot closed")
    except Exception as e:
        logger.debug(f"Telegram bot shutdown: {e}")

    # Close RabbitMQ connection
    if hasattr(app.state, "rabbitmq_connection") and app.state.rabbitmq_connection:
        try:
            await app.state.rabbitmq_connection.close()
            logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")
