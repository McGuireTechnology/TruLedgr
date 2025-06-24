from fastapi import APIRouter

accounts_router = APIRouter(prefix="/accounts", tags=["Accounts"])

@accounts_router.get("/test")
async def accounts_test():
    return {"status": "ok"}