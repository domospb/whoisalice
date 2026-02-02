# WhoIsAlice

AI Voice Assistant with Text-to-Speech (TTS) and Speech-to-Text (STT) support.

## Features

- 🎙️ **Voice Processing**: STT (Speech-to-Text) and TTS (Text-to-Speech)
- 🔐 **Authentication**: JWT-based user authentication
- 💰 **Balance System**: Credit-based payment system
- 📊 **Transaction History**: Track all operations
- 🤖 **Telegram Bot**: Full-featured bot interface
- 🌐 **REST API**: Complete API with Swagger docs

## Services

- **app** - FastAPI application
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
nano .env
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

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

### Test Telegram Bot

1. Start bot: `docker-compose exec app python -m src.api.telegram.bot`
2. Open Telegram and find your bot
3. Try commands: `/start`, `/register`, `/login`, etc.

## Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build
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
│   │   ├── domain/               # Domain models
│   │   ├── db/                   # Database layer
│   │   │   ├── models/           # ORM models
│   │   │   └── repositories/     # Data access
│   │   └── main.py               # FastAPI app
│   ├── init_db.py                # DB initialization
│   ├── test_operations.py        # DB tests
│   └── requirements.txt
├── web-proxy/                    # Nginx
├── volumes/                      # Storage
│   ├── audio/                    # Uploaded audio
│   └── results/                  # Generated audio
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

