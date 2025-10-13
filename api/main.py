from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .routers import auth, users, oauth, config

app = FastAPI(
    title="TruLedgr API",
    version="0.1.0",
    description="Personal finance application API"
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(oauth.router)
app.include_router(config.router)

# Configure CORS
# Allow origins can be set via ALLOWED_ORIGINS env (comma-separated).
allowed = os.getenv("ALLOWED_ORIGINS")
if allowed:
    allowed_origins = [o.strip() for o in allowed.split(",") if o.strip()]
else:
    # sensible defaults for staging/production and local dev
    allowed_origins = [
        "https://dash.truledgr.app",
        "https://truledgr-dash-new-sx2si.ondigitalocean.app",
        "http://localhost:8000",
        "http://localhost:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Bonjour from TruLedgr API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Bonjour, TruLedgr is running!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
