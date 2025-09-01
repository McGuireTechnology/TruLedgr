from fastapi import FastAPI
from .config import settings
from .routers import health, example


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(example.router, prefix="/api", tags=["example"])

    return app


app = create_app()
