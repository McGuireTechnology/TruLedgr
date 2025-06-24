from fastapi import APIRouter

categories_router = APIRouter(prefix="/categories", tags=["Categories"])

@categories_router.get("/test")
async def categories_test():
    return {"status": "ok"}