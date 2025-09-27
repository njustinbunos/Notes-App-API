from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, List

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)

    # db relationship, one user can have many notes
    notes: List["Note"] = Relationship(back_populates="owner")


class NoteBase(SQLModel):
    body: str
    color_id: str
    color_header: str
    color_body: str
    color_text: str
    pos_x: int
    pos_y: int


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
