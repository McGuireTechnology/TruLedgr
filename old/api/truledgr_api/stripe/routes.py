from fastapi import APIRouter

stripe_router = APIRouter(prefix="/stripe", tags=["Stripe"])

@stripe_router.get("/test")
async def stripe_test():
    return {"status": "ok"}