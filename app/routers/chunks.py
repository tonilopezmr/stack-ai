from fastapi import APIRouter, HTTPException
from app.models import Chunk
from app.routers import chunk_service

router = APIRouter()

@router.post("/libraries/{library_id}/documents/{document_id}/chunks")
def create_chunk(library_id: int, document_id: int, chunk: Chunk):
    new_chunk = chunk_service.create(library_id, document_id, chunk)
    return new_chunk

@router.get("/libraries/{library_id}/chunks/{chunk_id}")
def read_chunk(library_id: int, chunk_id: int):
    return chunk_service.read(library_id, chunk_id)   
    
@router.put("/libraries/{library_id}/chunks/{chunk_id}")
def update_chunk(library_id: int, chunk_id: int, chunk: Chunk):
    return chunk_service.update(library_id, chunk_id, chunk)    

@router.delete("/libraries/{library_id}/chunks/{chunk_id}")
def delete_chunk(library_id: int, chunk_id: int):
    return chunk_service.delete(library_id, chunk_id)
    