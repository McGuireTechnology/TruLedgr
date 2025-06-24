from fastapi import APIRouter

finicity_router = APIRouter(prefix="/finicity", tags=["Finicity"])

@finicity_router.get("/")
async def read_root():
    return {"message": "Welcome to the Finicity API"}

@finicity_router.get("/status")
async def get_status():
    return {"status": "Finicity API is up and running"}

@finicity_router.get("/test")
async def finicity_test():
    return {"status": "ok"}