# Start from official Python 3.12 image (slim version to keep size small)
FROM python:3.12-slim

# Set the working directory inside container
# All subsequent commands will run from this directory
WORKDIR /app

# Install system dependencies needed for Python packages
# gcc - needed to compile some Python packages
# curl - needed for Docker healthcheck
# Clean up apt cache after to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first (Docker layer caching optimization)
# If requirements.txt doesn't change, this layer will be cached
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir keeps the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
# This comes last so code changes don't invalidate the pip install cache
COPY src/ ./src/

# Document that the container listens on port 8000
# (doesn't actually publish the port, just documentation)
EXPOSE 8000

# Command to run when container starts
# uvicorn - ASGI server for FastAPI
# src.main:app - path to FastAPI app instance
# --host 0.0.0.0 - listen on all network interfaces (required in Docker)
# --port 8000 - port to listen on
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
