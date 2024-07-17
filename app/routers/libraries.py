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
    return  library_service.read(library_id)
    
@router.put("/libraries/{library_id}")
def update_library(library_id: int, library: Library):
    updated_library = library_service.update(library_id, library)
    return updated_library

@router.delete("/libraries/{library_id}")
def delete_library(library_id: int):
    library_service.delete(library_id)
    return "ok"
