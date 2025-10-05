from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class TokenPayload(SQLModel):
    sub: Optional[int] = None  # Subject (user ID)
    exp: Optional[int] = None  # Expiration time
    iat: Optional[int] = None  # Issued at time
    type: Optional[str] = None  # Token type (access or refresh)

class UserBase(SQLModel):
    username: str = Field(min_length=3, max_length=30)
    email: str

class UserCreate(UserBase):
    password: str = Field(min_length=6)

class UserRead(UserBase):
    id: int

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False, min_length=3, max_length=30)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False) #must be encrypted
    notes: List["Note"] = Relationship(back_populates="owner")

class LoginRequest(SQLModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6)


class NoteBase(SQLModel):
    body: str = Field(min_length=1, max_length=500)
    color_id: str = Field(max_length=20)

    color_header: str = Field(max_length=7, regex="^#(?:[0-9a-fA-F]{3}){1,2}$")  # Hex color code
    color_body: str = Field(max_length=7, regex="^#(?:[0-9a-fA-F]{3}){1,2}$")  # Hex color code
    color_text: str = Field(max_length=7, regex="^#(?:[0-9a-fA-F]{3}){1,2}$")  # Hex color code
    
    pos_x: int = Field(ge=0, le=5000)
    pos_y: int = Field(ge=0, le=5000)


class Note(NoteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional["UserBase"] = Relationship(back_populates="notes")


class NoteCreate(NoteBase):
    pass


class NoteRead(NoteBase):
    id: int
    owner_id: Optional[int]


class NoteUpdate(SQLModel):
    body: Optional[str] = Field(default=None, min_length=1, max_length=500)
    color_id: Optional[str] = None
    color_header: Optional[str] = None
    color_body: Optional[str] = None
    color_text: Optional[str] = None
    pos_x: Optional[int] = Field(default=None, ge=0, le=5000)
    pos_y: Optional[int] = Field(default=None, ge=0, le=5000)
