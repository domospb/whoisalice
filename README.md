# WhoIsAlice

AI Voice Assistant with Text-to-Speech (TTS) and Speech-to-Text (STT) support.

## Services

- **web-proxy** - nginx reverse proxy
- **app** - FastAPI application
- **database** - PostgreSQL 16
- **rabbitmq** - message broker

## Setup

```bash
# Copy environment file
cp .env.example .env

# Change passwords in .env
nano .env

# Start services
docker-compose up -d

# Initialize database with demo data
cd app
python init_db.py

# Check status
docker-compose ps
```

## Usage

- API: http://localhost/
- Health: http://localhost/health
- RabbitMQ UI: http://localhost:15672

## Database

### Initialize with demo data

```bash
cd app
python init_db.py
```

**Demo data includes:**
- Demo user: `demo_user` ($100 balance)
- Demo admin: `admin` ($1000 balance)
- ML models: Whisper STT ($0.50), GPT-4 TTS ($1.00), Claude STT ($0.75), ElevenLabs TTS ($1.50)

### Test database operations

```bash
cd app
python test_operations.py
```

Tests: user creation, balance top-up, credit deduction, transaction history.

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
├── app/                    # FastAPI application
│   ├── src/
│   │   ├── domain/        # Domain models (business logic)
│   │   ├── db/            # Database (ORM models, repositories)
│   │   └── main.py        # Entry point
│   ├── init_db.py         # Database initialization script
│   └── test_operations.py # Test database operations
├── web-proxy/             # Nginx config
└── docker-compose.yml     # Services
```
