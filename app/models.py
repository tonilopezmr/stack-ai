from typing import List, Dict, Optional
from pydantic import BaseModel
from pydantic import field_validator

class Chunk(BaseModel):
    id: Optional[int] = None
    text: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, str]] = None

class Document(BaseModel):
    id: Optional[int] = None
    chunks: List[Chunk]
    metadata: Optional[Dict[str, str]] = None

class Library(BaseModel):
    id: Optional[int] = None
    documents: List[Document]
    metadata: Optional[Dict[str, str]] = None

    @field_validator('documents')
    def check_documents_not_empty(cls, v):
        if not v:
            raise ValueError('Library must contain at least one document.')
        return v