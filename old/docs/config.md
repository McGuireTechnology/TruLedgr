# Configuration Guide

This document explains how to configure your FastAPI/ASGI application for the TruLedgr backend.

## Environment Variables

Configuration is managed using environment variables, typically set in a `.env` file (not committed to version control). An example file, `.env.example`, should be provided for reference.

### Example `.env` file
```env
# FastAPI settings
FAST_API_NAME=TruLedgr
FAST_API_DEBUG=True

# Uvicorn/ASGI server settings
ASGI_HOST=0.0.0.0
ASGI_PORT=8000
ASGI_RELOAD=True
```

## Configuration Structure

Configuration is grouped in `backend/truledgr/core/config.py` using Pydantic models:

```python
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field

class FastAPISettings(BaseModel):
    name: str = Field("TruLedgr", env="FAST_API_NAME")
    debug: bool = Field(True, env="FAST_API_DEBUG")

class ASGISettings(BaseModel):
    host: str = Field("0.0.0.0", env="ASGI_HOST")
    port: int = Field(8000, env="ASGI_PORT")
    reload: bool = Field(True, env="ASGI_RELOAD")

class Settings(BaseSettings):
    app: FastAPISettings = FastAPISettings()
    uvicorn: ASGISettings = ASGISettings()

    class Config:
        env_file = "../.env"

settings = Settings()
```

## How it Works
- The `Settings` class loads environment variables from the `.env` file.
- FastAPI-related settings are grouped under `settings.app`.
- Uvicorn/ASGI server settings are grouped under `settings.uvicorn`.
- You can override any value by setting the corresponding environment variable.

## Usage in Code
You can access your settings in your FastAPI app like this:

```python
from .core.config import settings

app = FastAPI(title=settings.app.name, debug=settings.app.debug)

# When running with uvicorn programmatically:
uvicorn.run(
    "truledgr.main:app",
    host=settings.uvicorn.host,
    port=settings.uvicorn.port,
    reload=settings.uvicorn.reload
)
```

## Best Practices
- Do not commit your real `.env` file to version control. Use `.env.example` for reference.
- Document all required environment variables in your example file and/or this documentation.
- Use environment variables for all secrets and environment-specific configuration.

---

For more details, see the code in `backend/truledgr/core/config.py`.
