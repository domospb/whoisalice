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
from uuid import UUID

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from ...db.session import AsyncSessionLocal
from ...services.auth_service import AuthService
from ...services.balance_service import BalanceService
from ...services.audio_service import AudioService
from ...services.stt_service import STTService
from ...services.tts_service import TTSService
from ...services.prediction_service import PredictionService
from ...services.history_service import HistoryService

logger = logging.getLogger(__name__)

router = Router()

# Simple in-memory user session storage
# TODO: Stage 5 - Replace with proper session management
user_sessions = {}

logger.info("Telegram handlers initialized")


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command - Welcome message."""
    logger.info(f"User {message.from_user.id} started bot")

    welcome_text = (
        "🎙️ *Welcome to WhoIsAlice!*\n\n"
        "AI Voice Assistant for TTS and STT operations.\n\n"
        "*Commands:*\n"
        "/register <username> <email> <password> - Register\n"
        "/login <username> <password> - Login\n"
        "/balance - Check balance\n"
        "/topup <amount> - Top-up balance\n"
        "/history - View transaction history\n\n"
        "*Usage:*\n"
        "• Send text messages for text predictions\n"
        "• Send voice messages for audio predictions\n\n"
        "_Note: You must login first_"
    )

    await message.answer(welcome_text, parse_mode="Markdown")


@router.message(Command("register"))
async def cmd_register(message: Message):
    """Handle /register command."""
    logger.info(f"User {message.from_user.id} - /register")

    # Parse command: /register username email password
    parts = message.text.split(maxsplit=3)

    if len(parts) != 4:
        await message.answer(
            "❌ Usage: /register <username> <email> <password>\n"
            "Example: /register alice alice@example.com mypass123"
        )
        return

    _, username, email, password = parts

    async with AsyncSessionLocal() as session:
        auth_service = AuthService(session)

        try:
            user_data = await auth_service.register_user(
                username=username, email=email, password=password
            )

            logger.info(f"User registered via Telegram: {username}")

            await message.answer(
                f"✅ Registration successful!\n\n"
                f"Username: {user_data['username']}\n"
                f"Email: {user_data['email']}\n\n"
                f"Now login with: /login {username} <password>"
            )

        except ValueError as e:
            logger.warning(f"Registration failed: {e}")
            await message.answer(f"❌ Registration failed: {e}")
        except Exception as e:
            logger.error(f"Registration error: {e}")
            await message.answer("❌ Registration failed. Please try again.")


@router.message(Command("login"))
async def cmd_login(message: Message):
    """Handle /login command."""
    logger.info(f"User {message.from_user.id} - /login")

    # Parse command: /login username password
    parts = message.text.split(maxsplit=2)

    if len(parts) != 3:
        await message.answer(
            "❌ Usage: /login <username> <password>\n" "Example: /login alice mypass123"
        )
        return

    _, username, password = parts

    async with AsyncSessionLocal() as session:
        auth_service = AuthService(session)

        try:
            login_data = await auth_service.login(username=username, password=password)

            # Store session
            user_id = login_data["user"]["user_id"]
            user_sessions[message.from_user.id] = user_id

            logger.info(f"User logged in via Telegram: {username} ({user_id})")

            await message.answer(
                f"✅ Login successful!\n\n"
                f"Username: {login_data['user']['username']}\n"
                f"Role: {login_data['user']['role']}\n\n"
                "You can now:\n"
                "• Send text messages for predictions\n"
                "• Send voice messages for audio predictions\n"
                "• Use /balance, /topup, /history"
            )

        except ValueError as e:
            logger.warning(f"Login failed: {e}")
            await message.answer("❌ Invalid username or password")
        except Exception as e:
            logger.error(f"Login error: {e}")
            await message.answer("❌ Login failed. Please try again.")


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    """Handle /balance command."""
    logger.info(f"User {message.from_user.id} - /balance")

    # Check if user is logged in
    user_id = user_sessions.get(message.from_user.id)
    if not user_id:
        await message.answer("❌ Please login first: /login <username> <password>")
        return

    async with AsyncSessionLocal() as session:
        balance_service = BalanceService(session)

        try:
            balance_data = await balance_service.get_balance(UUID(user_id))

            await message.answer(
                f"💰 *Your Balance*\n\n"
                f"Balance: *${balance_data['balance']:.2f}* "
                f"{balance_data['currency']}\n\n"
                f"Top-up: /topup <amount>",
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Balance check error: {e}")
            await message.answer("❌ Failed to get balance. Please try again.")


@router.message(Command("topup"))
async def cmd_topup(message: Message):
    """Handle /topup command."""
    logger.info(f"User {message.from_user.id} - /topup")

    # Check if user is logged in
    user_id = user_sessions.get(message.from_user.id)
    if not user_id:
        await message.answer("❌ Please login first: /login <username> <password>")
        return

    # Parse command: /topup amount
    parts = message.text.split()

    if len(parts) != 2:
        await message.answer("❌ Usage: /topup <amount>\n" "Example: /topup 50")
        return

    try:
        amount = float(parts[1])
    except ValueError:
        await message.answer("❌ Invalid amount. Use a number (e.g., 50 or 10.5)")
        return

    async with AsyncSessionLocal() as session:
        balance_service = BalanceService(session)

        try:
            topup_data = await balance_service.topup_balance(UUID(user_id), amount)

            await message.answer(
                f"✅ *Top-up Successful!*\n\n"
                f"Amount: *+${amount:.2f}*\n"
                f"New Balance: *${topup_data['new_balance']:.2f}* "
                f"{topup_data['currency']}\n\n"
                f"Transaction ID: `{topup_data['transaction_id']}`",
                parse_mode="Markdown",
            )

        except ValueError as e:
            logger.warning(f"Top-up failed: {e}")
            await message.answer(f"❌ Top-up failed: {e}")
        except Exception as e:
            logger.error(f"Top-up error: {e}")
            await message.answer("❌ Top-up failed. Please try again.")


@router.message(Command("history"))
async def cmd_history(message: Message):
    """Handle /history command."""
    logger.info(f"User {message.from_user.id} - /history")

    # Check if user is logged in
    user_id = user_sessions.get(message.from_user.id)
    if not user_id:
        await message.answer("❌ Please login first: /login <username> <password>")
        return

    async with AsyncSessionLocal() as session:
        history_service = HistoryService(session)

        try:
            transactions = await history_service.get_transactions(UUID(user_id))

            if not transactions:
                await message.answer("📜 No transaction history yet.")
                return

            # Format transactions (last 10)
            text = "📜 *Transaction History* (last 10)\n\n"

            for tx in transactions[-10:]:
                emoji = "💰" if tx["type"] == "credit" else "💸"
                sign = "+" if tx["type"] == "credit" else "-"

                text += (
                    f"{emoji} *{sign}${tx['amount']:.2f}*\n"
                    f"   {tx['description']}\n"
                    f"   _{tx['timestamp'][:19]}_\n\n"
                )

            await message.answer(text, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"History error: {e}")
            await message.answer("❌ Failed to get history. Please try again.")


@router.message(F.text)
async def handle_text_message(message: Message):
    """Handle text messages - Text prediction."""
    logger.info(f"User {message.from_user.id} sent text: {message.text[:50]}")

    # Check if user is logged in
    user_id = user_sessions.get(message.from_user.id)
    if not user_id:
        await message.answer("❌ Please login first: /login <username> <password>")
        return

    # Process text prediction
    async with AsyncSessionLocal() as session:
        audio_service = AudioService()
        stt_service = STTService()
        tts_service = TTSService()
        prediction_service = PredictionService(
            session, audio_service, stt_service, tts_service
        )

        try:
            await message.answer("🤔 Processing your message...")

            result = await prediction_service.process_text_prediction(
                user_id=UUID(user_id),
                input_text=message.text,
                model_name="GPT-4 TTS",
            )

            response_text = (
                f"✅ *Prediction Complete*\n\n"
                f"Result: {result['result_text']}\n\n"
                f"Cost: ${result['cost']:.2f}\n"
                f"Task ID: `{result['task_id']}`"
            )

            await message.answer(response_text, parse_mode="Markdown")

            # TODO: Send audio response when TTS is real

        except ValueError as e:
            logger.warning(f"Text prediction failed: {e}")
            await message.answer(f"❌ Prediction failed: {e}")
        except Exception as e:
            logger.error(f"Text prediction error: {e}")
            await message.answer("❌ Prediction failed. Please try again.")


@router.message(F.voice)
async def handle_voice_message(message: Message):
    """Handle voice messages - Audio prediction."""
    logger.info(f"User {message.from_user.id} sent voice message")

    # Check if user is logged in
    user_id = user_sessions.get(message.from_user.id)
    if not user_id:
        await message.answer("❌ Please login first: /login <username> <password>")
        return

    # Download voice file
    voice = message.voice
    file_info = await message.bot.get_file(voice.file_id)

    # Download file bytes
    file_data = await message.bot.download_file(file_info.file_path)
    audio_bytes = file_data.read()

    # Process audio prediction
    async with AsyncSessionLocal() as session:
        audio_service = AudioService()
        stt_service = STTService()
        tts_service = TTSService()
        prediction_service = PredictionService(
            session, audio_service, stt_service, tts_service
        )

        try:
            await message.answer("🎙️ Processing your voice message...")

            result = await prediction_service.process_audio_prediction(
                user_id=UUID(user_id),
                audio_file=audio_bytes,
                filename=f"{voice.file_id}.ogg",
                model_name="Whisper STT",
            )

            response_text = (
                f"✅ *Audio Prediction Complete*\n\n"
                f"Transcription: _{result.get('transcription', 'N/A')}_\n\n"
                f"Result: {result['result_text']}\n\n"
                f"Cost: ${result['cost']:.2f}\n"
                f"Task ID: `{result['task_id']}`"
            )

            await message.answer(response_text, parse_mode="Markdown")

            # Send audio response
            audio_path = (
                result["audio_url"]
                .replace("/api/v1/predict/", "")
                .replace("/audio", "_result.ogg")
            )
            audio_file_path = f"volumes/results/{audio_path}"

            try:
                audio_file = FSInputFile(audio_file_path)
                await message.answer_voice(audio_file)
                logger.info(f"Audio response sent: {audio_file_path}")
            except Exception as e:
                logger.warning(f"Failed to send audio: {e}")

        except ValueError as e:
            logger.warning(f"Audio prediction failed: {e}")
            await message.answer(f"❌ Prediction failed: {e}")
        except Exception as e:
            logger.error(f"Audio prediction error: {e}")
            await message.answer("❌ Prediction failed. Please try again.")
