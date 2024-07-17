from fastapi import FastAPI
from app.routers import libraries, chunks

app = FastAPI()

app.include_router(libraries.router)
app.include_router(chunks.router)
