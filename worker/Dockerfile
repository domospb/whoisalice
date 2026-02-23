# Worker service - independent from app
# Only installs dependencies needed for ML task processing
FROM python:3.12-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy and install only worker dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Shared code (db, queue, services, core) is mounted via volumes
# Worker entry point is also mounted from app/src/

CMD ["python", "-m", "src.worker"]
