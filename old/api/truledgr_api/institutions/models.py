from sqlmodel import SQLModel, Field
import ulid

class Institution(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(ulid.new()), primary_key=True, index=True)