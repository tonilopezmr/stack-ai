from fastapi import APIRouter, HTTPException
from app.models import Library
from app.routers import library_service

router = APIRouter()

@router.post("/libraries")
def create_library(library: Library):
    created_library = library_service.create_library(library)
    return created_library

@router.get("/libraries/{library_id}")
def read_library(library_id: int):
    library = library_service.read_library(library_id)
    #if library is None:
    #    raise HTTPException(status_code=404, detail="Library not found")
        
    return library        
    

@router.put("/libraries/{library_id}")
def update_library(library_id: int, library: Library):
    updated_library = library_service.update_library(library_id, library)
    return updated_library

@router.delete("/libraries/{library_id}")
def delete_library(library_id: int):
    library_service.delete_library(library_id)
    return "ok"
