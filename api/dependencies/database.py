"""Database and Unit of Work dependencies."""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

from ..repositories.uow import SqlAlchemyUnitOfWork
from ..config.settings import get_settings

settings = get_settings()


# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True,
    pool_pre_ping=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Usage:
        @router.get("/users")
        async def get_users(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_uow(
    session: AsyncSession = Depends(get_db_session)
) -> SqlAlchemyUnitOfWork:
    """
    Dependency that provides a Unit of Work.
    
    The Unit of Work manages transactions across multiple repositories.
    
    Usage:
        @router.post("/users")
        async def create_user(
            uow: SqlAlchemyUnitOfWork = Depends(get_uow)
        ):
            async with uow:
                user = await uow.users.create(user)
                await uow.commit()
    """
    return SqlAlchemyUnitOfWork(session)
