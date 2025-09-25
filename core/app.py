from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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