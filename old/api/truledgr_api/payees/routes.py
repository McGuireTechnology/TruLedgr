from fastapi import APIRouter

payees_router = APIRouter(prefix="/payees", tags=["Payees"])

@payees_router.get("/test")
async def payees_test():
    return {"status": "ok"}