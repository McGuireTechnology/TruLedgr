from fastapi import APIRouter

institutions_router = APIRouter(prefix="/institutions", tags=["Institutions"])

@institutions_router.get("/test")
async def institutions_test():
    return {"status": "ok"}