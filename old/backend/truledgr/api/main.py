from fastapi import APIRouter

from .routes import items, login, private, users, utils
from ..core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)


if settings.include_private_routes:
    api_router.include_router(private.router)
