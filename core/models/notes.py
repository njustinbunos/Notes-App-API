from sqlmodel import SQLModel, Field, Relationship
from users import User
from typing import Optional

class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    body: str
    colors: str
    position: str

    # Foreign key
    owner_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="notes")
