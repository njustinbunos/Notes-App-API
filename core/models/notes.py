from sqlmodel import SQLModel, Field, Relationship
from users import User
from typing import Optional

class NoteBase(SQLModel):
    body: str
    color: str  
    position: str

class Note(NoteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="notes")

class NoteCreate(NoteBase):
    pass

class NoteRead(NoteBase):
    id: int
    owner_id: Optional[int]

# Input: when updating
class NoteUpdate(SQLModel):
    body: Optional[str] = None
    color: Optional[str] = None  
    position: Optional[str] = None
