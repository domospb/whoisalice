from fastapi import FastAPI

app = FastAPI(
    title="WhoIsAlice ML Service",
    description="AI Voice Assistant - TTS and STT operations",
    version="0.1.0",
)


@app.get("/")
async def root():
    """Root endpoint - service information."""
    return {
        "service": "WhoIsAlice",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
