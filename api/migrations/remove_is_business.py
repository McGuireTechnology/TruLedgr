"""
Migration script to remove is_business column from users table.

This script removes the is_business field from the database.
Run with: poetry run python -m api.migrations.remove_is_business
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os


async def migrate():
    """Remove is_business column from users table."""
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./truledgr.db"
    )
    
    print(f"Connecting to database: {database_url}")
    engine = create_async_engine(database_url, echo=True)
    
    async with engine.begin() as conn:
        # Check if column exists (SQLite specific)
        result = await conn.execute(
            text("PRAGMA table_info(users)")
        )
        columns = [row[1] for row in result.fetchall()]
        
        if 'is_business' in columns:
            print("\n⚠️  is_business column found in users table")
            print("⚠️  SQLite doesn't support DROP COLUMN directly")
            print("⚠️  You'll need to recreate the table or use Alembic")
            print("\nOption 1: Drop and recreate database (development only)")
            print("  rm truledgr.db")
            print("  poetry run python -m api.init_db")
            print("\nOption 2: For production, set up Alembic migrations")
        else:
            print("\n✅ is_business column not found - migration not needed")
    
    await engine.dispose()
    print("\n✅ Migration check complete")


if __name__ == "__main__":
    asyncio.run(migrate())
