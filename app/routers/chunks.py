from fastapi import APIRouter, HTTPException
from app.models import Chunk
from app.routers import chunk_service

router = APIRouter()

@router.post("/libraries/{library_id}/documents/{document_id}/chunks")
def create_chunk(library_id: int, document_id: int, chunk: Chunk):
    new_chunk = chunk_service.add_chunk(library_id, document_id, chunk)
    return new_chunk

@router.get("/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}")
def read_chunk(library_id: int, document_id: int, chunk_id: int):
    chunk = chunk_service.read_chunk(library_id, document_id, chunk_id)
    #if chunk is None:
    #    raise HTTPException(status_code=404, detail="Chunk not found")
    
    return chunk
