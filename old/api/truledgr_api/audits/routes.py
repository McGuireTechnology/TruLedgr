from fastapi import APIRouter

audits_router = APIRouter(prefix="/audits", tags=["Audits"])

@audits_router.get("/test")
async def audits_test():
    return {"status": "ok"}