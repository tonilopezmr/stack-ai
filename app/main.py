from fastapi import FastAPI
from app.routers import libraries, chunks, vector

app = FastAPI()

app.include_router(libraries.router)
app.include_router(chunks.router)
app.include_router(vector.router)


@app.get("/")
def read_root():
    return {"message": "@tonilopezmr Stack AI!"}
