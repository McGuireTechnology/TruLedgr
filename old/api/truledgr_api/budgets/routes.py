from fastapi import APIRouter

budgets_router = APIRouter(prefix="/budgets", tags=["Budgets"])

@budgets_router.get("/test")
async def budgets_test():
    return {"status": "ok"}