from fastapi import FastAPI, Depends, Path, Query, HTTPException
from sqlmodel import Session, select
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .models import Note, NoteBase, NoteCreate, NoteRead, NoteUpdate, UserBase, UserCreate, LoginRequest, User
from .utils.jwt import create_access_token, create_refresh_token, verify_token_type, decode_token, get_token_expiration, create_token_pair
from .utils.security import hash_password, verify_password

from .database import initialize_db, get_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_db()
    yield   


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://localhost:3000"],  # Or whathever the host of my React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Message":"Hello World!"}

@app.post("/register")
async def register(credentials: UserCreate, session: Session = Depends(get_session)):
    try:
        db_user = session.exec(
            select(User).where(User.username == credentials.username)).first()
        if db_user:
            raise HTTPException(
                status_code=400, 
                detail="Username already registered"
            )

        db_user = session.exec(
            select(User).where(User.email == credentials.email)
        ).first()
        if db_user:
            raise HTTPException(
                status_code=400, 
                detail="Email already registered"
            )

        new_user = User(
            username=credentials.username,
            email=credentials.email,
            password_hash=hash_password(credentials.password)
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return {"Message": "Register endpoint"}
    except Exception as e:
        # put e in a log file
        raise HTTPException(status_code=500, detail="Failed to register user")

@app.post("/login")
async def login(credentials: LoginRequest, session: Session = Depends(get_session)):
    try:
        user_query = select(User).where(User.username == credentials.username)  # Changed from UserBase to User
        found_user = session.exec(user_query).first()
        if not found_user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        if not verify_password(credentials.password, found_user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        access_token = create_access_token({"sub": found_user.username})
        refresh_token = create_refresh_token({"sub": found_user.username})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        # put e in a log file
        raise HTTPException(status_code=500, detail="Failed to login user")
    
@app.post("/notes/", response_model=NoteRead)
async def create_notes(note: NoteCreate, session: Session = Depends(get_session)):
    try:
        db_note = Note.model_validate(note)

        session.add(db_note)
        session.commit()
        session.refresh(db_note)

        return db_note
    except Exception as e:
        # put e in a log file
        raise HTTPException(status_code=500, detail="Failed to create note")

        

@app.get("/notes/", response_model=list[NoteRead])
async def get_notes(session: Session = Depends(get_session)):
    try:
        notes = session.exec(select(Note)).all()
        return notes
    except Exception as e:
        # pput e in a log file
        raise HTTPException(status_code=500, detail="Failed to fetch notes")

@app.get("/notes/{note_id}", response_model=NoteRead)
async def get_note(note_id: int = Path(ge=1), session: Session = Depends(get_session)):
    try:
        note = session.get(Note, note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    except Exception as e:
        # put e in a log file
        raise HTTPException(status_code=500, detail="Failed to fetch note")

@app.put("/notes/{note_id}", response_model=NoteRead)
async def update_note(
    note_update: NoteUpdate,
    note_id: int = Path(ge=1),
    session: Session = Depends(get_session)
):
    try:
        db_note = session.get(Note, note_id)
        if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")

        note_data = note_update.model_dump(exclude_unset=True)
        for key, value in note_data.items():
            setattr(db_note, key, value)

        session.add(db_note)
        session.commit()
        session.refresh(db_note)

        return db_note
    except Exception as e:
        # put e in a log file
        raise HTTPException(status_code=500, detail="Failed to update note")
    
@app.delete("/notes/{note_id}")
async def delete_note(
    note_id: int = Path(ge=1),
    session: Session = Depends(get_session)
):
    try:
        db_note = session.get(Note, note_id)
        if not db_note:
            raise HTTPException(status_code=404, detail="Note not found")

        session.delete(db_note)
        session.commit()

        return {"detail": "Note deleted"}
    except Exception as e:
        # put e in a log file
        raise HTTPException(status_code=500, detail="Failed to delete note")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

