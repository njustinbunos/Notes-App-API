from fastapi import FastAPI, Depends, Path, Query, HTTPException
from sqlmodel import Session, select
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import *

from database.connection import initialize_db, get_session

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

@app.post("/notes/", response_model=Note)
async def create_notes(note: NoteCreate, session: Session = Depends(get_session)):
    db_note = Note.model_validate(note)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note

@app.get("/notes/")
async def get_notes():
    return {"Notes":"a list of notes or smth"}

