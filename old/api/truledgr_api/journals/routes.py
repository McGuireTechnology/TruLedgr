from fastapi import APIRouter

journals_router = APIRouter(prefix="/journals", tags=["Journals"])

@journals_router.get("/test")
async def journals_test():
    return {"status": "ok"}