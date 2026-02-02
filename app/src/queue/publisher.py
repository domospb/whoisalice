"""
RabbitMQ publisher for ML tasks.

Publishes ML task messages to the queue for worker processing.
"""
import json
import logging
from uuid import UUID

from aio_pika import Message
from aio_pika.abc import AbstractChannel

logger = logging.getLogger(__name__)

QUEUE_NAME = "ml_tasks"


class TaskPublisher:
    """Publisher for ML task messages."""

    def __init__(self, channel: AbstractChannel):
        """
        Initialize publisher with RabbitMQ channel.

        Args:
            channel: RabbitMQ channel
        """
        self.channel = channel
        self.queue_name = QUEUE_NAME
        logger.info(f"TaskPublisher initialized for queue: {self.queue_name}")

    async def setup_queue(self):
        """
        Declare the task queue.

        Creates a durable queue if it doesn't exist.
        """
        logger.info(f"Declaring queue: {self.queue_name}")

        queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True,  # Survive broker restart
        )

        logger.info(
            f"Queue declared: {self.queue_name} "
            f"(messages: {queue.declaration_result.message_count})"
        )

        return queue

    async def publish_task(
        self,
        task_id: UUID,
        user_id: UUID,
        model_id: UUID,
        input_data: str,
        input_type: str,
        output_type: str,
    ) -> bool:
        """
        Publish ML task to queue.

        Args:
            task_id: Task UUID
            user_id: User UUID
            model_id: ML Model UUID
            input_data: Input data (text or file path)
            input_type: Type of input (text or audio)
            output_type: Type of output (text or audio)

        Returns:
            True if published successfully

        Raises:
            Exception: If publishing fails
        """
        logger.info(f"Publishing task {task_id} to queue")

        # Create message payload
        message_data = {
            "task_id": str(task_id),
            "user_id": str(user_id),
            "model_id": str(model_id),
            "input_data": input_data,
            "input_type": input_type,
            "output_type": output_type,
        }

        logger.debug(f"Message payload: {message_data}")

        try:
            # Convert to JSON
            message_body = json.dumps(message_data).encode()

            # Create message with persistence
            message = Message(
                body=message_body,
                delivery_mode=2,  # Persistent message
                content_type="application/json",
            )

            # Publish to queue
            await self.channel.default_exchange.publish(
                message,
                routing_key=self.queue_name,
            )

            logger.info(
                f"Task {task_id} published successfully to queue: {self.queue_name}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to publish task {task_id}: {e}")
            raise
