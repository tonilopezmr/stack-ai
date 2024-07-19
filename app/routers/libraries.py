from fastapi import APIRouter, HTTPException
from app.models import Library
from app.routers import library_service

router = APIRouter()

@router.post("/libraries")
def create_library(library: Library):
    created_library = library_service.create(library)
    return created_library

@router.get("/libraries/{library_id}")
def read_library(library_id: int):
    library = library_service.read(library_id)
    
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    return library
@router.delete("/libraries/{library_id}")
def delete_library(library_id: int):
    library_service.delete(library_id)
    return "ok"
