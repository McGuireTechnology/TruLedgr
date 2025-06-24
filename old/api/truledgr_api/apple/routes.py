from fastapi import APIRouter

apple_router = APIRouter(prefix="/apple", tags=["Apple"])

@apple_router.get("/test")
async def apple_test():
    return {"status": "ok"}