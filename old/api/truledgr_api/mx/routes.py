from fastapi import APIRouter

mx_router = APIRouter(prefix="/mx", tags=["MX"])

@mx_router.get("/test")
async def mx_test():
    return {"status": "ok"}