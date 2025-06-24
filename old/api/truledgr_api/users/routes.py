from fastapi import APIRouter

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/test")
async def users_test():
    return {"status": "ok"}