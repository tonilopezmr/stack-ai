from typing import List, Dict, Optional, TypeAlias, Any
from pydantic import BaseModel
from pydantic import field_validator

Metadata: TypeAlias = Dict[str, Any]

class Chunk(BaseModel):
    id: Optional[int] = None
    text: str
    embedding: List[float]
    metadata: Optional[Metadata] = None

class Document(BaseModel):
    id: Optional[int] = None
    chunks: List[Chunk]
    metadata: Optional[Metadata] = None

class Library(BaseModel):
    id: Optional[int] = None
    documents: List[Document]
    metadata: Optional[Metadata] = None

    @field_validator('documents')
    def check_documents_not_empty(cls, v):
        if not v:
            raise ValueError('Library must contain at least one document.')
        return v

class QueryVector(BaseModel):
    vector: List[float]
    num_results: int = 5
    filter_metadata: Optional[Metadata] = None

class StackAIError(Exception):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code