from typing import List, Dict, Optional
from pydantic import BaseModel

class Chunk(BaseModel):
    id: Optional[int] = None
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, str]

class Document(BaseModel):
    id: Optional[int] = None
    chunks: List[Chunk]
    metadata: Dict[str, str]

class Library(BaseModel):
    id: Optional[int] = None
    documents: List[Document]
    metadata: Dict[str, str]
