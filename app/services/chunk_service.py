from app.models import Chunk, Document, Library
from app.storage import ChunkDataSource

class ChunkService:
    def __init__(self, chunk_datasource: ChunkDataSource):
        self.chunks = chunk_datasource

    def create(self, library_id: int, document_id: int, chunk: Chunk):
        return self.chunks.add(library_id, document_id, chunk)

    def read(self, library_id: int, document_id: int, chunk_id: int):
        return self.chunks.get(library_id, document_id, chunk_id)

    def update(self, library_id: int, document_id: int, chunk_id: int, chunk: Chunk):
        return self.chunks.update(library_id, document_id, chunk_id, chunk)

    def delete(self, library_id: int, document_id: int, chunk_id: int):
        return self.chunks.remove(library_id, document_id, chunk_id)
