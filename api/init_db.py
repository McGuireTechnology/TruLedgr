"""Initialize database tables.

This script creates the database tables using SQLAlchemy's metadata.
For production, use Alembic migrations instead.
"""

import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine

# Add parent directory to path to import api package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.repositories.models import Base


async def init_db():
    """Create all database tables."""
    # Load database URL from environment or use default
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./truledgr.db"
    )
    
    print(f"Initializing database: {database_url}")
    
    engine = create_async_engine(
        database_url,
        echo=True
    )
    
    async with engine.begin() as conn:
        # Drop all tables (use with caution!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
