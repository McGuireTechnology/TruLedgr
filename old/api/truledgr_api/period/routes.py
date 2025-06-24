from fastapi import APIRouter

period_router = APIRouter(prefix="/period", tags=["Period"])


@period_router.get("/test")
async def period_test():
    return {"status": "ok"}