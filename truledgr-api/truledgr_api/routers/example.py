from fastapi import APIRouter
from typing import Optional

router = APIRouter()


@router.get("/hello")
async def hello(name: Optional[str] = None):
    return {"message": f"Hello {name or 'world'}"}
