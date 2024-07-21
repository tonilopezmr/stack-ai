from fastapi import APIRouter, HTTPException
from app.models import Document
from app.routers import document_service

router = APIRouter()

@router.post("/libraries/{library_id}/documents")
def create_document(library_id: int, document: Document):
    new_document = document_service.create(library_id, document)
    return new_document

@router.get("/libraries/{library_id}/documents/{document_id}")
def read_document(library_id: int, document_id: int):
    document = document_service.read(library_id, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.put("/libraries/{library_id}/documents/{document_id}")
def update_document(library_id: int, document_id: int, document: Document):
    document.id = document_id
    return document_service.update(library_id, document)

@router.delete("/libraries/{library_id}/documents/{document_id}")
def delete_document(library_id: int, document_id: int):        
    document = document_service.delete(library_id, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document
