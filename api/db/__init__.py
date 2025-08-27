"""
Database package for SQLModel/SQLAlchemy async operations.

This package provides:
- base: SQLModel metadata and table creation utilities
- session: Database engine and session management
- seed: Initial data seeding for roles, permissions, and admin user
- deps: Database dependency injection for FastAPI
"""

from .base import Base, create_tables, drop_tables
from .session import engine, get_async_session, SessionLocal
from .deps import get_db

__all__ = [
    "Base",
    "create_tables", 
    "drop_tables",
    "engine",
    "get_async_session",
    "SessionLocal",
    "get_db"
]
