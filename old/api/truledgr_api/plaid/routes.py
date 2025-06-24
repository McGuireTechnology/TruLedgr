from fastapi import APIRouter

plaid_router = APIRouter(prefix="/plaid", tags=["Plaid"])

@plaid_router.get("/test")
async def plaid_test():
    return {"status": "ok"}