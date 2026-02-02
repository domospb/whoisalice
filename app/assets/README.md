# Assets

This directory contains static assets for the application.

## mock_response.ogg

Placeholder audio file for mock TTS responses in Stage 4.

To create a simple silent OGG file for testing:
```bash
ffmpeg -f lavfi -i anullsrc=r=24000:cl=mono -t 1 -acodec libopus mock_response.ogg
```

Or record a simple message like "This is a mock response from WhoIsAlice".
