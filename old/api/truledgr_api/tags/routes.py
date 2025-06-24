from fastapi import APIRouter

tags_router = APIRouter(prefix="/tags", tags=["Tags"])

@tags_router.get("/test")
async def tags_test():
    return {"status": "ok"}