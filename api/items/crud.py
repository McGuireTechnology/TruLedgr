from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from .models import Item
from typing import List, Optional

async def get_item(db: AsyncSession, item_id: int) -> Optional[Item]:
    result = await db.execute(select(Item).where(Item.id == item_id))
    return result.scalar_one_or_none()

async def list_items(db: AsyncSession) -> List[Item]:
    result = await db.execute(select(Item))
    return list(result.scalars().all())

async def create_item(db: AsyncSession, item: Item) -> Item:
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

async def update_item(db: AsyncSession, item_id: int, item_data: dict) -> Optional[Item]:
    item = await get_item(db, item_id)
    if not item:
        return None
    for key, value in item_data.items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item

async def delete_item(db: AsyncSession, item_id: int) -> bool:
    item = await get_item(db, item_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True
