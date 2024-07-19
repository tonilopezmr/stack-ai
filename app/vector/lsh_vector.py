import numpy as np
from app.models import StackAIError
from app.vector.vector_store import VectorStore

class LSHVectorStore(VectorStore):
    def __init__(self, num_hash_tables=5, hash_size=10, input_dim=128):
        super().__init__()
        self.num_hash_tables = num_hash_tables
        self.hash_size = hash_size
        self.input_dim = input_dim
        self.hash_tables = [{} for _ in range(num_hash_tables)]        
        self.random_vectors = [np.random.randn(hash_size, input_dim) for _ in range(num_hash_tables)]

    def _hash_vector(self, vector, random_vectors):
        return tuple((np.dot(random_vectors, vector) > 0).astype(int))

    def add_vector_store(self, store_id: int):
        if store_id not in self.vector_stores:
            self.vector_stores[store_id] = {
                'vector_data': {},
                'metadata': {}
            }

    def delete_vector_store(self, store_id: int):
        if store_id in self.vector_stores:
            del self.vector_stores[store_id]
            for table in self.hash_tables:
                keys_to_delete = [key for key in table if key[0] == store_id]
                for key in keys_to_delete:
                    del table[key]

    def add_vector(self, store_id: int, vector_id: int, vector: list[float], metadata: dict = None):
        if store_id in self.vector_stores:
            self.vector_stores[store_id]['vector_data'][vector_id] = vector
            if metadata:
                self.vector_stores[store_id]['metadata'][vector_id] = metadata
            for i, random_vectors in enumerate(self.random_vectors):
                hash_key = self._hash_vector(vector, random_vectors)
                if (store_id, hash_key) not in self.hash_tables[i]:
                    self.hash_tables[i][(store_id, hash_key)] = []
                self.hash_tables[i][(store_id, hash_key)].append(vector_id)

    def update_vector(self, store_id: int, vector_id: int, new_vector: list[float], metadata: dict = None):
        self.delete_vector(store_id, vector_id)
        self.add_vector(store_id, vector_id, new_vector, metadata)

    def get_vector(self, store_id: int, vector_id: int):
        if store_id in self.vector_stores:
            return self.vector_stores[store_id]['vector_data'].get(vector_id)

    def delete_vector(self, store_id: int, vector_id: int):
        if store_id in self.vector_stores and vector_id in self.vector_stores[store_id]['vector_data']:
            vector = self.vector_stores[store_id]['vector_data'][vector_id]
            del self.vector_stores[store_id]['vector_data'][vector_id]
            if vector_id in self.vector_stores[store_id]['metadata']:
                del self.vector_stores[store_id]['metadata'][vector_id]
            for i, random_vectors in enumerate(self.random_vectors):
                hash_key = self._hash_vector(vector, random_vectors)
                if (store_id, hash_key) in self.hash_tables[i]:
                    self.hash_tables[i][(store_id, hash_key)].remove(vector_id)
                    if not self.hash_tables[i][(store_id, hash_key)]:
                        del self.hash_tables[i][(store_id, hash_key)]

    def find_similar_vectors(self, store_id: int, query_vector: list[float], num_results: int = 5, metadata_filter: dict = None, space: str = 'cosine') -> list[float]:
        if store_id not in self.vector_stores:
            return None

        candidate_vectors = set()
        for i, random_vectors in enumerate(self.random_vectors):            
            hash_key = self._hash_vector(query_vector, random_vectors)            
            if (store_id, hash_key) in self.hash_tables[i]:
                candidate_vectors.update(self.hash_tables[i][(store_id, hash_key)])

        if not candidate_vectors:
            return []

        vector_data = self.vector_stores[store_id]['vector_data']
        metadata = self.vector_stores[store_id]['metadata']
        similarities = []

        for vector_id in candidate_vectors:
            vector = vector_data[vector_id]
            if len(query_vector) != len(vector):
                raise StackAIError("Query vector length does not match the length of the chunk embeddings.", error_code=400)

            if metadata_filter and self._metadata_matches(metadata[vector_id], metadata_filter):
                continue

            similarity = self._calculate_similarity(query_vector, vector, space)
            similarities.append((vector_id, similarity))

        similarities.sort(key=lambda x: x[1], reverse=(space == 'cosine'))
        return similarities[:num_results]
