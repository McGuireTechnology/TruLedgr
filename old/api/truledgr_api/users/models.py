from sqlmodel import SQLModel, Field
import ulid

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(ulid.new()), primary_key=True, index=True)
    user_id (PK)
    email
    name
    created_at