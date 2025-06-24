from fastapi import APIRouter

documents_router = APIRouter(prefix="/documents", tags=["Documents"])

@documents_router.get("/test")
async def documents_test():
    return {"status": "ok"}