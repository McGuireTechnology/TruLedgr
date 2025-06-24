from fastapi import APIRouter, HTTPException, status, Body, Depends
import requests
from sqlmodel import Session
from ..database import get_session
from .models import WalmartReceiptLookupRequest, WalmartStore

walmart_router = APIRouter(prefix="/walmart", tags=["Walmart"])

@walmart_router.post("/receipt-lookup", status_code=status.HTTP_200_OK)
async def receipt_lookup(
    body: WalmartReceiptLookupRequest = Body(..., description="Walmart receipt lookup request")
):
    params = body.dict()
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.4 Safari/605.1.15",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.walmart.com/receipt-lookup"
    }
    try:
        resp = requests.get(
            "https://www.walmart.com/chcwebapp/api/receipts",
            params=params,
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Walmart API error: {str(e)}")


@walmart_router.post("/stores", status_code=status.HTTP_201_CREATED)
async def create_store(store: WalmartStore, session: Session = Depends(get_session)):
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


@walmart_router.get("/stores/{store_id}", response_model=WalmartStore)
async def get_store(store_id: str, session: Session = Depends(get_session)):
    store = session.get(WalmartStore, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@walmart_router.get("/stores", response_model=list[WalmartStore])
async def list_stores(session: Session = Depends(get_session)):
    stores = session.exec(WalmartStore.select()).all()
    return stores


@walmart_router.get("/test")
async def walmart_test():
    return {"status": "ok"}
