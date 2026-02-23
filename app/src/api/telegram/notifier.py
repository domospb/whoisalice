"""
Background task: send Telegram notifications when ML tasks complete or fail.
"""
import asyncio
import json
import logging
from pathlib import Path

from aiogram.types import FSInputFile

from src.api.telegram.bot import bot
from src.core.config import settings
from src.db.repositories.ml_task import MLTaskRepository
from src.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Telegram message length limit
MAX_MESSAGE_LENGTH = 4096
NOTIFIER_INTERVAL_SEC = 10


def _build_notification_text(task) -> str:
    """Build notification message for a completed or failed task (plain text)."""
    if task.status == "completed":
        lines = [
            "✅ Task completed",
            f"Task ID: {task.id}",
            f"Model: {task.model.name if task.model else 'Unknown'}",
        ]
        if task.result and task.result.prediction_data:
            try:
                data = json.loads(task.result.prediction_data)
                if data.get("transcription"):
                    tr = data["transcription"][:500]
                    lines.append(f"Transcription: {tr}")
                if data.get("output"):
                    out = data["output"]
                    if len(out) > 800:
                        out = out[:797] + "..."
                    lines.append(f"Reply: {out}")
            except (json.JSONDecodeError, TypeError):
                pass
        return "\n".join(lines)
    else:
        # failed (plain text so underscores in error_message don't break Telegram)
        lines = [
            "❌ Task failed",
            f"Task ID: {task.id}",
            f"Model: {task.model.name if task.model else 'Unknown'}",
        ]
        # Show partial result (transcription + reply) if TTS failed after STT/Chat
        if task.result and task.result.prediction_data:
            try:
                data = json.loads(task.result.prediction_data)
                if data.get("partial") and data.get("transcription"):
                    tr = data["transcription"][:400]
                    lines.append(f"Transcription: {tr}")
                if data.get("partial") and data.get("output"):
                    out = data["output"][:400]
                    lines.append(f"Reply (text): {out}")
            except (json.JSONDecodeError, TypeError):
                pass
        if task.error_message:
            err = task.error_message
            if len(err) > 500:
                err = err[:497] + "..."
            lines.append(f"Error: {err}")
        return "\n".join(lines)


def _get_audio_result_path(task) -> Path | None:
    """Return path to audio result file if task has one and file exists."""
    if not task.result or not task.result.prediction_data:
        return None
    try:
        data = json.loads(task.result.prediction_data)
        path_str = data.get("audio_result")
        if not path_str:
            return None
        # Worker saves to volumes/audio_uploads/<task_id>_result.wav
        p = Path(path_str)
        if not p.is_absolute():
            p = Path(settings.AUDIO_UPLOAD_DIR) / p.name
        return p if p.exists() else None
    except (json.JSONDecodeError, TypeError):
        return None


async def _send_pending_notifications() -> None:
    """Fetch pending notifications, send Telegram messages, mark notified."""
    if not bot:
        logger.debug("Notifier: bot not configured, skipping")
        return
    async with AsyncSessionLocal() as session:
        repo = MLTaskRepository(session)
        tasks = await repo.get_pending_notifications()
        logger.info("Notifier: found %s pending notification(s)", len(tasks))
        for task in tasks:
            if not task.telegram_chat_id:
                logger.warning("Notifier: task %s has no telegram_chat_id, skipping", task.id)
                continue
            try:
                # Optionally send voice reply first (so user gets audio in chat)
                audio_path = _get_audio_result_path(task)
                if audio_path and task.status == "completed":
                    try:
                        await bot.send_audio(
                            chat_id=task.telegram_chat_id,
                            audio=FSInputFile(str(audio_path)),
                            caption="🎙️ Reply (audio)",
                        )
                        logger.info(
                            "Notifier: sent audio for task %s to chat %s",
                            task.id,
                            task.telegram_chat_id,
                        )
                    except Exception as e:
                        logger.warning(
                            "Notifier: failed to send audio for task %s: %s",
                            task.id,
                            e,
                        )
                text = _build_notification_text(task)
                if len(text) > MAX_MESSAGE_LENGTH:
                    text = text[: MAX_MESSAGE_LENGTH - 3] + "..."
                await bot.send_message(
                    chat_id=task.telegram_chat_id,
                    text=text,
                )
                await repo.mark_notified(task.id)
                logger.info(
                    "Sent Telegram notification for task %s to chat %s",
                    task.id,
                    task.telegram_chat_id,
                )
            except Exception as e:
                logger.exception(
                    "Failed to send Telegram notification for task %s: %s",
                    task.id,
                    e,
                )


async def run_notifier_loop() -> None:
    """
    Run the notification loop: every NOTIFIER_INTERVAL_SEC seconds,
    send pending task notifications to Telegram.
    """
    logger.info(
        "Task notification loop started (interval=%ss)", NOTIFIER_INTERVAL_SEC
    )
    while True:
        try:
            await asyncio.sleep(NOTIFIER_INTERVAL_SEC)
            await _send_pending_notifications()
        except asyncio.CancelledError:
            logger.info("Task notification loop cancelled")
            raise
        except Exception as e:
            logger.exception("Notification loop error: %s", e)
