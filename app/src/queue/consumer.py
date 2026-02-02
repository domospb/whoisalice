"""
RabbitMQ consumer for ML tasks.

Base consumer class for ML task workers.
"""
import json
import logging
from typing import Callable

from aio_pika import IncomingMessage
from aio_pika.abc import AbstractChannel

logger = logging.getLogger(__name__)

QUEUE_NAME = "ml_tasks"


class TaskConsumer:
    """Consumer for ML task messages."""

    def __init__(
        self, channel: AbstractChannel, callback: Callable, worker_id: str = "worker-1"
    ):
        """
        Initialize consumer with RabbitMQ channel and callback.

        Args:
            channel: RabbitMQ channel
            callback: Async function to process messages
            worker_id: Unique worker identifier
        """
        self.channel = channel
        self.callback = callback
        self.worker_id = worker_id
        self.queue_name = QUEUE_NAME

        logger.info(
            f"TaskConsumer initialized: {worker_id} for queue: {self.queue_name}"
        )

    async def setup_queue(self):
        """
        Declare and bind to the task queue.

        Returns:
            Queue instance
        """
        logger.info(f"Worker {self.worker_id}: Declaring queue {self.queue_name}")

        queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True,  # Survive broker restart
        )

        logger.info(
            f"Worker {self.worker_id}: Queue declared "
            f"(messages: {queue.declaration_result.message_count})"
        )

        return queue

    async def process_message(self, message: IncomingMessage):
        """
        Process incoming message.

        Args:
            message: RabbitMQ message
        """
        async with message.process():
            logger.info(
                f"Worker {self.worker_id}: Received message "
                f"(delivery_tag={message.delivery_tag})"
            )

            try:
                # Parse message body
                message_data = json.loads(message.body.decode())

                logger.debug(
                    f"Worker {self.worker_id}: Parsed message: "
                    f"task_id={message_data.get('task_id')}"
                )

                # Call the processing callback
                await self.callback(message_data, self.worker_id)

                logger.info(
                    f"Worker {self.worker_id}: Message processed successfully "
                    f"(task_id={message_data.get('task_id')})"
                )

            except json.JSONDecodeError as e:
                logger.error(f"Worker {self.worker_id}: Invalid JSON: {e}")
                # Message will be rejected (not requeued)

            except Exception as e:
                logger.error(
                    f"Worker {self.worker_id}: Message processing error: {e}"
                )
                # Message will be rejected (not requeued)
                raise

    async def start_consuming(self):
        """
        Start consuming messages from queue.

        Runs indefinitely until stopped.
        """
        logger.info(f"Worker {self.worker_id}: Starting to consume messages...")

        # Setup queue
        queue = await self.setup_queue()

        # Start consuming
        await queue.consume(self.process_message)

        logger.info(
            f"Worker {self.worker_id}: Consuming messages from {self.queue_name}"
        )
