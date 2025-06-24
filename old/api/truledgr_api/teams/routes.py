from fastapi import APIRouter

teams_router = APIRouter(prefix="/teams", tags=["Teams"])

@teams_router.get("/test")
async def teams_test():
    return {"status": "ok"}