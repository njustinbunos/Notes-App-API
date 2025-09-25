from fastapi import FastAPI, Depends, Path, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

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

@app.get("/notes/")
async def get_notes():
    return {"Notes":"a list of notes or smth"}

@app.post("/notes/")
async def create_notes():
    #create notes
    pass