from fastapi import APIRouter

transactions_router = APIRouter(prefix="/transactions", tags=["Transactions"])

@transactions_router.get("/test")
async def transactions_test():
    return {"status": "ok"}