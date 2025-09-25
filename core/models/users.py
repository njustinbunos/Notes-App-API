from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from notes import Note

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)

    # db relationship, one user can have many notes
    notes: List["Note"] = Relationship(back_populates="owner")
