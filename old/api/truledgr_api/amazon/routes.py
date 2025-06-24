from fastapi import APIRouter

amazon_router = APIRouter(prefix="/amazon", tags=["Amazon"])

@amazon_router.get("/test")
async def amazon_test():
    return {"status": "ok"}