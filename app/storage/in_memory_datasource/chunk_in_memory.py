from app.models import Chunk
from .. import ChunkDataSource
from .library_in_memory import LibraryInMemoryDatasource
from typing import Optional
import threading

class ChunkInMemoryDatasource(ChunkDataSource):
    def __init__(self, library_datasource: LibraryInMemoryDatasource):
        self.libraries = library_datasource
        self.lock = threading.Lock()

    def add(self, library_id: int, document_id: int, chunk: Chunk) -> Optional[Chunk]:
        with self.lock:
            library = self.libraries.get(library_id)
        
            if library:
                for doc in library.documents:
                    if doc.id == document_id:
                        doc.chunks.append(chunk)
                        return chunk            

    def get(self, library_id: int, chunk_id: int) -> Optional[Chunk]:
        with self.lock:
            library = self.libraries.get(library_id)
            if library:
                for doc in library.documents:                
                    for chunk in doc.chunks:
                        if chunk.id == chunk_id:
                            return chunk
                

    def update(self, library_id: int, chunk: Chunk) -> Optional[Chunk]:
        with self.lock:
            library = self.libraries.get(library_id)
            if library:
                for doc in library.documents:                
                    for i, existing_chunk in enumerate(doc.chunks):
                        if existing_chunk.id == chunk.id:
                            doc.chunks[i] = chunk
                            return chunk

    def remove(self, library_id: int, chunk_id: int) -> Optional[Chunk]:
        with self.lock:
            library = self.libraries.get(library_id)
            if library:
                for doc in library.documents:                
                    for i, chunk in enumerate(doc.chunks):
                        if chunk.id == chunk_id:
                            del doc.chunks[i]
                            return chunk        