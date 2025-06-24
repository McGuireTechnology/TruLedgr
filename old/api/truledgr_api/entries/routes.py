from fastapi import APIRouter

entries_router = APIRouter(prefix="/entries", tags=["Entries"])


@entries_router.get("/test")
async def entries_test():
    return {"status": "ok"}