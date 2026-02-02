"""
RabbitMQ connection management.

Handles connection to RabbitMQ broker.
"""
import logging
from typing import Optional

import aio_pika
from aio_pika import Channel
from aio_pika.abc import AbstractRobustConnection

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    """RabbitMQ connection manager."""

    def __init__(
        self,
        host: str = "rabbitmq",
        port: int = 5672,
        username: str = "guest",
        password: str = "changeme_strong_password",
    ):
        """
        Initialize RabbitMQ connection parameters.

        Args:
            host: RabbitMQ host
            port: RabbitMQ port
            username: Username
            password: Password
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel: Optional[Channel] = None

        logger.info(f"RabbitMQ connection configured: {host}:{port}")

    async def connect(self) -> AbstractRobustConnection:
        """
        Establish connection to RabbitMQ.

        Returns:
            RabbitMQ connection

        Raises:
            ConnectionError: If connection fails
        """
        logger.info(f"Connecting to RabbitMQ at {self.host}:{self.port}...")

        try:
            self.connection = await aio_pika.connect_robust(
                host=self.host,
                port=self.port,
                login=self.username,
                password=self.password,
            )

            logger.info("RabbitMQ connection established")

            return self.connection

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise ConnectionError(f"RabbitMQ connection failed: {e}")

    async def get_channel(self) -> Channel:
        """
        Get or create a channel.

        Returns:
            RabbitMQ channel

        Raises:
            ConnectionError: If not connected
        """
        if not self.connection:
            logger.error("Not connected to RabbitMQ")
            raise ConnectionError("Not connected to RabbitMQ. Call connect() first.")

        if not self.channel or self.channel.is_closed:
            logger.debug("Creating new channel")
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)  # Fair dispatch
            logger.info("Channel created with QoS: prefetch_count=1")

        return self.channel

    async def close(self):
        """Close connection to RabbitMQ."""
        logger.info("Closing RabbitMQ connection...")

        if self.channel and not self.channel.is_closed:
            await self.channel.close()
            logger.debug("Channel closed")

        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")


# Global connection instance
rabbitmq_connection = RabbitMQConnection()


async def get_rabbitmq_connection() -> RabbitMQConnection:
    """
    Get global RabbitMQ connection instance.

    Returns:
        RabbitMQ connection manager
    """
    return rabbitmq_connection
