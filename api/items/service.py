from . import crud
from .models import Item
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional

async def get_item(db: AsyncSession, item_id: int) -> Optional[Item]:
    return await crud.get_item(db, item_id)

async def list_items(db: AsyncSession) -> List[Item]:
    return await crud.list_items(db)

async def create_item(db: AsyncSession, item: Item) -> Item:
    return await crud.create_item(db, item)

async def update_item(db: AsyncSession, item_id: int, item_data: dict) -> Optional[Item]:
    return await crud.update_item(db, item_id, item_data)

async def delete_item(db: AsyncSession, item_id: int) -> bool:
    return await crud.delete_item(db, item_id)
