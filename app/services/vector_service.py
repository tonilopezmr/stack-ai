from app.models import QueryVector
from app.storage import LibraryDataSource, ChunkDataSource
from app.vector import VectorStore


class VectorService:
    def __init__(self, library_datasource: LibraryDataSource, chunk_datasource: ChunkDataSource, vector_store: VectorStore):
        self.library_datasource = library_datasource
        self.chunks = chunk_datasource
        self.vector_store = vector_store

    def search_similar_sentences(self, library_id: int, query_vector: QueryVector):
        if not self.vector_store.vector_store_exists(library_id):
            # vector_store works as a cache, if the vector is not in the cache, we need to recompute the vector
            library = self.library_datasource.get(library_id)
            if not library:
                return None

            self.vector_store.add_vector_store(library.id)
            self.vector_store.add_library_chunks_if_needed(library)            

        similar_vectors = self.vector_store.find_similar_vectors(library_id, query_vector.vector, query_vector.num_results, query_vector.filter_metadata)        

        result = []
        for vector in similar_vectors:
            chunk = self.chunks.get(library_id, vector[0])
            result.append((chunk.text, vector[1]))

        return result
