from fastapi import APIRouter, HTTPException, Depends, status, Body
from sqlmodel.ext.asyncio.session import AsyncSession
from api.db.session import get_async_session
from .models import Item, ItemCreate, ItemUpdate
from . import service
from typing import List

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("", response_model=List[Item])
async def list_items(db: AsyncSession = Depends(get_async_session)):
    return await service.list_items(db)

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int, db: AsyncSession = Depends(get_async_session)):
    item = await service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate = Body(...), db: AsyncSession = Depends(get_async_session)):
    db_item = Item.from_orm(item)
    return await service.create_item(db, db_item)

@router.patch("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate = Body(...), db: AsyncSession = Depends(get_async_session)):
    item_data = item.dict(exclude_unset=True)
    updated = await service.update_item(db, item_id, item_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_async_session)):
    deleted = await service.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return None
