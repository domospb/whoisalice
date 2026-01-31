# WhoIsAlice

AI Voice Assistant with Text-to-Speech (TTS) and Speech-to-Text (STT) support.

## Services

- **web-proxy** - nginx reverse proxy
- **app** - FastAPI application
- **database** - PostgreSQL 16
- **rabbitmq** - message broker

## Setup

```bash
# Copy environment files
cp .env.example .env
cp app/.env.example app/.env

# Change passwords in .env files
nano .env
nano app/.env

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

## Usage

- API: http://localhost/
- Health: http://localhost/health
- RabbitMQ UI: http://localhost:15672

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
├── app/                 # FastAPI application
│   ├── src/domain/     # Domain models
│   └── src/main.py     # Entry point
├── web-proxy/          # Nginx config
└── docker-compose.yml  # Services
```
