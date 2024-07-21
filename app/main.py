from fastapi import FastAPI
from app.routers import libraries, chunks, vector, documents

app = FastAPI()

app.include_router(libraries.router)
app.include_router(chunks.router)
app.include_router(vector.router)
app.include_router(documents.router)


@app.get("/")
def read_root():
    return {"message": "@tonilopezmr Stack AI!"}
