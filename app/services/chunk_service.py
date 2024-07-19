from app.models import Chunk
from app.storage import ChunkDataSource
from app.vector import VectorStore

class ChunkService:
    def __init__(self, chunk_datasource: ChunkDataSource, vector_store: VectorStore):
        self.chunks = chunk_datasource
        self.vector_store = vector_store

    def create(self, library_id: int, document_id: int, chunk: Chunk):
        new_chunk = self.chunks.add(library_id, document_id, chunk)
        self.vector_store.add_vector(library_id, new_chunk.id, new_chunk.embedding, chunk.metadata)
        return new_chunk

    def read(self, library_id: int, chunk_id: int):
        return self.chunks.get(library_id, chunk_id)

    def update(self, library_id: int, chunk_id: int, chunk: Chunk):
        updated_chunk = self.chunks.update(library_id, chunk_id, chunk)
        self.vector_store.update_vector(library_id, chunk_id, chunk.embedding, chunk.metadata)
        return updated_chunk

    def delete(self, library_id: int, chunk_id: int):
        return self.chunks.remove(library_id, chunk_id)
