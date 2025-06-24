from sqlmodel import SQLModel, Field
from typing import Optional, Any
from datetime import datetime
import ulid

class Audit(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(ulid.new()), primary_key=True, index=True)
    date: datetime = Field(default_factory=datetime.utcnow, index=True)
    entity_type: str
    entity_id: str
    user_id: Optional[str] = None
    action: str
    before: Optional[Any] = None  # Use JSON type if your DB supports it
    after: Optional[Any] = None   # Use JSON type if your DB supports it
    context: Optional[Any] = None # Use JSON type if your DB supports it