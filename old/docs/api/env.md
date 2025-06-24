# Environment Variables Reference for TruLedgr Backend

This document describes all environment variables used in the backend, as defined in `truledgr/core/config.py`.

---

## General
- **DEBUG**: (bool, default: `False`)
  - Global debug flag. Used as fallback for FastAPI and Uvicorn debug/reload if not set explicitly.

## FastAPI
- **FASTAPI_NAME**: (str, default: `TruLedgr`)
  - The title/name of the FastAPI application.
- **FASTAPI_DEBUG**: (bool, default: value of `DEBUG`)
  - Enables FastAPI debug mode (detailed error pages, etc.).

## Uvicorn
- **UVICORN_HOST**: (str, default: `0.0.0.0`)
  - Host address for Uvicorn server.
- **UVICORN_PORT**: (int, default: `8000`)
  - Port for Uvicorn server.
- **UVICORN_RELOAD**: (bool, default: value of `DEBUG`)
  - Enables Uvicorn's auto-reload (for development).

## CORS Middleware
- **CORS_ALLOWED_ORIGINS**: (list[str], default: `[]`)
  - List of allowed origins for CORS. Should be a JSON array, e.g. `["http://localhost"]`.
- **CORS_ALLOW_CREDENTIALS**: (bool, default: `True`)
  - Whether to allow credentials in CORS.
- **CORS_ALLOW_METHODS**: (list[str], default: `["*"]`)
  - List of allowed HTTP methods for CORS. Should be a JSON array.
- **CORS_ALLOW_HEADERS**: (list[str], default: `["*"]`)
  - List of allowed HTTP headers for CORS. Should be a JSON array.

## SQL Alchemy
- **SQLALCHEMY_DB_URL**: (str, required)
  - Database connection string for SQLAlchemy/SQLModel.

## Sentry
- **SENTRY_DSN**: (str, optional)
  - Sentry Data Source Name (DSN) for error tracking. Leave blank to disable Sentry.
- **SENTRY_DEFAULT_PII**: (bool, default: `True`)
  - Whether to send personally identifiable information to Sentry.
- **SENTRY_TRACES_SAMPLE_RATE**: (float, default: `1.0`)
  - Sentry performance traces sample rate.
- **SENTRY_PROFILE_SESSION_SAMPLE_RATE**: (float, default: `1.0`)
  - Sentry profile session sample rate.
- **SENTRY_PROFILE_LIFECYCLE**: (str, default: `trace`)
  - Sentry profile lifecycle mode.

---

**Note:**
- Boolean and list values should be provided as JSON (e.g., `true`, `false`, `["*"]`).
- If a value is not set in the environment, the default from `config.py` will be used.
- For development, set `DEBUG=true`, `FASTAPI_DEBUG=true`, and `UVICORN_RELOAD=true`.
- For production, set `DEBUG=false`, `FASTAPI_DEBUG=false`, and `UVICORN_RELOAD=false`.

---

For more details, see the code in `truledgr/core/config.py`.
