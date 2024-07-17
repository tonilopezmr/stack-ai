from app.models import Chunk, Document, Library
from . import LibraryService

class ChunkService:
    def __init__(self, library_service: LibraryService):
        self.libraries = library_service

    def add_chunk(self, library_id: int, document_id: int, chunk: Chunk):
        library = self.libraries.read_library(library_id)
    
        if library:
            for doc in library.documents:
                if doc.id == document_id:
                    doc.chunks.append(chunk)
                    return chunk
        
        return None

    def read_chunk(self, library_id: int, document_id: int, chunk_id: int):
        library = self.libraries.read_library(library_id)
        if library:
            for doc in library.documents:
                if doc.id == document_id:
                    for chunk in doc.chunks:
                        if chunk.id == chunk_id:
                            return chunk
