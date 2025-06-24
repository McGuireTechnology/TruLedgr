from fastapi import APIRouter

goals_router = APIRouter(prefix="/goals", tags=["Goals"])

@goals_router.get("/test")
async def goals_test():
    return {"status": "ok"}