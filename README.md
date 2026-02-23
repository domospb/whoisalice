# WhoIsAlice

AI Voice Assistant with Text-to-Speech (TTS) and Speech-to-Text (STT) support.

**Stage 5**: Asynchronous ML task processing with RabbitMQ workers.

## Features

- 🎙️ **Voice Processing**: STT (Speech-to-Text) and TTS (Text-to-Speech)
- 🔐 **Authentication**: JWT-based user authentication
- 💰 **Balance System**: Credit-based payment system
- 📊 **Transaction History**: Track all operations
- 🤖 **Telegram Bot**: Full-featured bot interface
- 🌐 **REST API**: Complete API with Swagger docs
- ⚡ **Async Processing**: RabbitMQ queue with multiple workers (Stage 5)

## Services

- **app** - FastAPI application (publisher)
- **worker** - ML task workers (consumers, scalable)
- **web-proxy** - Nginx reverse proxy
- **database** - PostgreSQL 16
- **rabbitmq** - RabbitMQ message broker

## Quick Start

### 1. Setup Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env and set:
# - Strong passwords for POSTGRES_PASSWORD and RABBITMQ_DEFAULT_PASS
# - SECRET_KEY for JWT (generate with: openssl rand -hex 32)
# - TELEGRAM_BOT_TOKEN (get from @BotFather)
# - HUGGINGFACE_API_TOKEN with **Make calls to Inference Providers** (fine-grained token)
#   Create: https://huggingface.co/settings/tokens → Fine-grained → enable Inference
nano .env
```

### 2. Start Services

```bash
# Start all services (including 2 workers by default)
docker-compose up -d

# Or start with custom number of workers
docker-compose up -d --scale worker=3

# Initialize database with demo data
cd app
python init_db.py
```

### 3. Access Services

- **REST API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **RabbitMQ UI**: http://localhost:15672
- **Telegram Bot**: Use your bot from @BotFather

## Setting up Yandex TTS (optional)

By default, TTS uses **Hugging Face** Inference Providers. To use **Yandex SpeechKit** TTS instead, follow these steps.

### Step 1: Create a Yandex Cloud account

1. Go to [Yandex Cloud](https://cloud.yandex.com/) and sign in or register.
2. Create a **billing account** and link a payment method (required for SpeechKit; there is a free tier).

### Step 2: Create a folder and enable SpeechKit

1. In the [Yandex Cloud Console](https://console.cloud.yandex.com/), create a **folder** (e.g. `whoisalice`) if you don’t have one.
2. Open **SpeechKit** in the catalog: [SpeechKit](https://console.cloud.yandex.com/folders/<FOLDER_ID>/speechkit) (replace `<FOLDER_ID>` with your folder ID).
3. Enable the service if prompted.

### Step 3: Create a service account and API key

Do this in the [Yandex Cloud Console](https://console.cloud.yandex.com/). Replace `<FOLDER_ID>` below with your folder ID (you see it in the console URL or in the folder list).

#### 3.1 Open Service accounts

1. In the left sidebar, open **All services** (or the menu icon).
2. Under **Management**, click **IAM** (Identity and Access Management).
3. In the IAM page, open the **Service accounts** tab.
   - Direct link: `https://console.cloud.yandex.com/folders/<FOLDER_ID>/service-accounts`

#### 3.2 Create a service account

1. Click **Create service account** (top right).
2. **Name**: e.g. `whoisalice-tts` (any name you like).
3. **Description** (optional): e.g. `TTS for WhoIsAlice`.
4. Click **Add role** and assign a role that allows SpeechKit:
   - In the role list, find **SpeechKit** (or search for `speechkit`).
   - Select **SpeechKit User** (role id: `ai.speechkit-stt.user` — it covers both STT and TTS).
   - If you don’t see “SpeechKit User”, look for **SpeechKit** → **User** or any role that grants access to SpeechKit API.
5. Click **Create** at the bottom. The new service account appears in the list.

#### 3.3 Create an API key for the service account

1. In the **Service accounts** list, click the name of the service account you just created (e.g. `whoisalice-tts`).
2. Open the **API keys** tab.
3. Click **Create API key**.
4. **Description** (optional): e.g. `WhoIsAlice TTS`.
5. Click **Create**. A dialog shows the key:
   - **Key ID** (for reference only).
   - **Secret key** — this is your API key. Copy it immediately; it is shown only once and cannot be viewed again.
6. Paste the secret key into a secure place (password manager or your `.env` file as `YANDEX_API_KEY=...`). Then close the dialog.

You’re done with Step 3. Use the copied value as `YANDEX_API_KEY` in Step 4.

### Step 4: Configure the app

1. In your project root, copy the example env and open `.env`:
   ```bash
   cp .env.example .env
   nano .env   # or your editor
   ```
2. Set TTS to Yandex and add your key and options:
   ```env
   TTS_PROVIDER=yandex
   YANDEX_API_KEY=your-api-key-from-step-3
   YANDEX_TTS_VOICE=filipp
   YANDEX_TTS_LANG=ru-RU
   ```
   - **YANDEX_API_KEY** (required): The API key from Step 3.
   - **YANDEX_FOLDER_ID**: Leave empty when using a service account API key (Yandex uses the key’s folder automatically). Only set when using IAM token instead of API key.
   - **YANDEX_TTS_VOICE**: Voice name, e.g. `filipp`, `alena`, `john` (English). Full list: [SpeechKit voices](https://cloud.yandex.com/docs/speechkit/tts/voices).
   - **YANDEX_TTS_LANG**: Language code: `ru-RU`, `en-US`, `de-DE`, etc.

3. Restart the app and workers so they load the new env:
   ```bash
   docker compose up -d --build
   ```

### Step 5: Verify

- Send a voice or text prediction that triggers TTS (e.g. voice message via Telegram or REST).
- Check worker logs: `docker compose logs worker` — you should see `TTSService initialized: Yandex SpeechKit (voice=..., lang=...)`.
- If you get 401/403, check the API key and that the service account has the SpeechKit role.

To switch back to Hugging Face TTS, set `TTS_PROVIDER=huggingface` (or remove `YANDEX_API_KEY`) and restart.

## Usage

### REST API

**1. Register a new user:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "mypass123"}'
```

**2. Login and get token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "mypass123"}'
```

**3. Use API with token:**
```bash
# Check balance
curl -X GET http://localhost:8000/api/v1/balance \
  -H "Authorization: Bearer YOUR_TOKEN"

# Top-up balance
curl -X POST http://localhost:8000/api/v1/balance/topup \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100}'

# Text prediction
curl -X POST http://localhost:8000/api/v1/predict/text \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, WhoIsAlice!", "model_name": "GPT-4 TTS"}'
```

**Or use Swagger UI:** http://localhost:8000/docs

### Stage 5: Async Processing with Workers

**How it works:**
1. API/Bot receives prediction request
2. Creates MLTask in database (status=pending)
3. Publishes task to RabbitMQ queue
4. Returns task_id immediately to user
5. Workers consume tasks from queue
6. Workers process task, deduct balance, save results
7. Task status updated: pending → processing → completed/failed

**Submit a task:**
```bash
# Text prediction (returns task_id immediately)
curl -X POST http://localhost:8000/api/v1/predict/text \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, WhoIsAlice!", "model_name": "GPT-4 TTS"}'

# Response: {"task_id": "uuid", "status": "pending", "cost": 1.0}
```

**Check task status:**
```bash
# Get task result (check status and result)
curl -X GET http://localhost:8000/api/v1/predict/{task_id} \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response includes: status (pending/processing/completed/failed)
```

**View prediction history:**
```bash
curl -X GET http://localhost:8000/api/v1/history/predictions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Scale workers:**
```bash
# Scale up to 5 workers
docker-compose up -d --scale worker=5

# Scale down to 1 worker
docker-compose up -d --scale worker=1

# View worker logs
docker-compose logs -f worker
```

### Telegram Bot

**Start the bot:**
```bash
docker-compose exec app python -m src.api.telegram.bot
```

**Commands:**
- `/start` - Welcome message
- `/register <username> <email> <password>` - Register
- `/login <username> <password>` - Login
- `/balance` - Check balance
- `/topup <amount>` - Top-up balance
- `/history` - View transaction history

**Usage:**
- Send text messages for text predictions
- Send voice messages for audio predictions

### Demo Data

**Demo users:**
- Username: `demo_user`, Password: `hashed_demo_password`, Balance: $100
- Username: `admin`, Password: `hashed_admin_password`, Balance: $1000

**ML Models:**
- Whisper STT - $0.50 per prediction
- GPT-4 TTS - $1.00 per prediction
- Claude STT - $0.75 per prediction
- ElevenLabs TTS - $1.50 per prediction

## Testing

### Test Database Operations

```bash
cd app
python test_operations.py
```

### Test REST API

Use Swagger UI at http://localhost:8000/docs or curl commands above.

### Test Stage 5: Async Workers

**1. Check RabbitMQ Management UI:**
- Open http://localhost:15672 (guest/guest)
- Go to "Queues" tab
- See `ml_tasks` queue

**2. Submit multiple tasks:**
```bash
# Login and get token first
TOKEN="your_jwt_token_here"

# Submit 5 tasks in a row
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/predict/text \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"Test message $i\", \"model_name\": \"GPT-4 TTS\"}"
  echo ""
done
```

**3. Watch workers process tasks:**
```bash
# View worker logs (you'll see round-robin distribution)
docker-compose logs -f worker

# Expected output:
# worker-1 | Processing task: abc-123...
# worker-2 | Processing task: def-456...
# worker-1 | Processing task: ghi-789...
```

**4. Verify results:**
```bash
# Check predictions history
curl -X GET http://localhost:8000/api/v1/history/predictions \
  -H "Authorization: Bearer $TOKEN"

# Check specific task status
curl -X GET http://localhost:8000/api/v1/predict/{task_id} \
  -H "Authorization: Bearer $TOKEN"
```

**5. Test scaling:**
```bash
# Scale to 5 workers
docker-compose up -d --scale worker=5

# Submit more tasks and watch distribution
docker-compose logs -f worker
```

### Test Telegram Bot

1. Start bot: `docker-compose exec app python -m src.api.telegram.bot`
2. Open Telegram and find your bot
3. Try commands: `/start`, `/register`, `/login`, etc.
4. Send text/voice messages and receive task_id
5. Tasks are processed asynchronously by workers

## Troubleshooting

### Tasks stay PENDING

1. **Workers not running**  
   ```bash
   docker compose ps
   ```
   Ensure `worker` service is up. Restart: `docker compose up -d worker`.

2. **Worker logs**  
   ```bash
   docker compose logs worker
   ```
   Look for "Consuming messages from ml_tasks" and any connection/import errors.

3. **RabbitMQ**  
   Open http://localhost:15672 → Queues → `ml_tasks`. Check "Ready" messages (unconsumed). If messages pile up, workers are not consuming.

### Hugging Face token not used / 403 / 404

- Inference uses **Hugging Face Inference Providers** (router); requires `huggingface_hub>=0.31` and a **fine-grained** token with **"Make calls to Inference Providers"** (not only Read).
- Create: https://huggingface.co/settings/tokens → "+ Create new token" → **Fine-grained** → under **Inference** enable **"Make calls to Inference Providers"**.
- Set `HUGGINGFACE_API_TOKEN` in `.env` and restart: `docker compose up -d`. Rebuild images after upgrading deps: `docker compose up -d --build`.
- **Inference provider**: Default is **Together AI** (`HF_PROVIDER=together`). Enable it at **https://hf.co/settings/inference-providers** so the router can route requests. Text model: [zai-org/GLM-5](https://huggingface.co/zai-org/GLM-5?inference_provider=together). Image-to-text: [moonshotai/Kimi-K2.5](https://huggingface.co/moonshotai/Kimi-K2.5?inference_provider=together). STT stays Whisper (`HF_STT_MODEL=openai/whisper-large-v3`).
- **402 Payment Required**: If the router picks a paid provider, add credits at https://huggingface.co/settings/billing.
- **"Model not available" / 404**: Set `HF_CHAT_MODEL`, `HF_IMAGE_TO_TEXT_MODEL`, `HF_STT_MODEL`, or `HF_TTS_MODEL` in `.env` to a model supported by your provider. Links: [STT](https://huggingface.co/models?pipeline_tag=automatic-speech-recognition), [TTS](https://huggingface.co/models?pipeline_tag=text-to-speech), [Chat](https://huggingface.co/models?pipeline_tag=conversational), [Vision](https://huggingface.co/models?pipeline_tag=image-text-to-text).
- **TTS: Yandex SpeechKit**: To use Yandex TTS, set `TTS_PROVIDER=yandex` and `YANDEX_API_KEY` in `.env`. See [Setting up Yandex TTS](#setting-up-yandex-tts-optional) above. If Yandex returns 401/403, check the API key and service account role (`SpeechKit User`).

## Commands

```bash
# Start all services
docker-compose up -d

# Start with custom number of workers
docker-compose up -d --scale worker=3

# Stop
docker-compose down

# View logs
docker-compose logs -f              # All services
docker-compose logs -f app          # API only
docker-compose logs -f worker       # All workers

# Rebuild
docker-compose up -d --build

# Restart workers only
docker-compose restart worker
```

## Project Structure

```
whoisalice/
├── app/
│   ├── src/
│   │   ├── api/                  # API interfaces
│   │   │   ├── rest/             # REST API endpoints
│   │   │   ├── telegram/         # Telegram bot
│   │   │   └── schemas/          # Pydantic schemas
│   │   ├── core/                 # Core utilities
│   │   │   ├── config.py         # Settings
│   │   │   └── security.py       # JWT, passwords
│   │   ├── services/             # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── balance_service.py
│   │   │   ├── prediction_service.py
│   │   │   └── ...
│   │   ├── queue/                # RabbitMQ (Stage 5)
│   │   │   ├── connection.py     # RabbitMQ connection
│   │   │   ├── publisher.py      # Task publisher
│   │   │   └── consumer.py       # Task consumer base
│   │   ├── domain/               # Domain models
│   │   ├── db/                   # Database layer
│   │   │   ├── models/           # ORM models
│   │   │   └── repositories/     # Data access
│   │   ├── worker.py             # ML Worker (Stage 5)
│   │   └── main.py               # FastAPI app
│   ├── init_db.py                # DB initialization
│   ├── test_operations.py        # DB tests
│   └── requirements.txt
├── web-proxy/                    # Nginx
├── volumes/                      # Storage
│   ├── audio_uploads/            # Uploaded audio
│   └── audio_results/            # Generated audio
├── docker-compose.yml
└── .env                          # Configuration
```

## Development

### Local Development

```bash
# Install dependencies
cd app
uv pip install -r requirements.txt

# Run FastAPI
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run Telegram bot
python -m src.api.telegram.bot
```

### Docker Development

```bash
# Rebuild and restart
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Execute commands in container
docker-compose exec app python init_db.py
```

