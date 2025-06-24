from fastapi import APIRouter

ledgers_router = APIRouter(prefix="/ledgers", tags=["Ledgers"])

@ledgers_router.get("/test")
async def ledgers_test():
    return {"status": "ok"}