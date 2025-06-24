from fastapi import FastAPI
from .routes import api_router

app = FastAPI(
    title="TruLedgr API",
    description="API backend for the TruLedgr project.",
    version="1.0.0"
)

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the TruLedgr API!"}
