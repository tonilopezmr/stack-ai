from app.models import QueryVector
from app.storage import ChunkDataSource
from app.vector import VectorStore

class VectorService:
    def __init__(self, chunk_datasource: ChunkDataSource, vector_store: VectorStore):
        self.chunks = chunk_datasource
        self.vector_store = vector_store

    def search_similar_sentences(self, library_id: int, query_vector: QueryVector):
        similar_vectors = self.vector_store.find_similar_vectors(library_id, query_vector.vector, query_vector.num_results, query_vector.filter_metadata)

        if not similar_vectors:
            return None

        result = []
        for vector in similar_vectors:
            chunk = self.chunks.get(library_id, vector[0])
            result.append((chunk.text, vector[1]))

        return result
