from fastapi import FastAPI, Depends, Path, Query, HTTPException
from sqlmodel import Session, select
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .models import Note, NoteBase, NoteCreate, NoteRead, NoteUpdate

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

