from fastapi import FastAPI
from fastapi.middleware import cors

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Message":"Hello World!"}