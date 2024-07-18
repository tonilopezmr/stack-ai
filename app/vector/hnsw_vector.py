
from app.vector.vector_store import VectorStore
from app.models import StackAIError

class HNSWVectorStore(VectorStore):
    def __init__(self, space='cosine', dim=128):
        super().__init__()
        self.space = space
        self.dim = dim
        self.max_elements = 10000
        self.ef_construction = 200
        self.M = 16
        self.ef = 50

    def add_vector_store(self, store_id: int):
        if store_id not in self.vector_stores:
            self.vector_stores[store_id] = {
                'vector_data': {},
                'vector_index': {},
                'metadata': {}
            }

    def delete_vector_store(self, store_id: int):
        if store_id in self.vector_stores:
            del self.vector_stores[store_id]

    def get_vector(self, store_id: int, vector_id: int):
        if store_id in self.vector_stores:
            vector_data = self.vector_stores[store_id]['vector_data']
            return vector_data.get(vector_id, None)        

    def add_vector(self, store_id: int, vector_id: int, vector: list[float], metadata: dict = None):
        if store_id in self.vector_stores:
            vector_data = self.vector_stores[store_id]['vector_data']
            index = self.vector_stores[store_id]['vector_index']
            metadata_store = self.vector_stores[store_id]['metadata']
            if vector_id not in vector_data:
                vector_data[vector_id] = vector
                if metadata:
                    metadata_store[vector_id] = metadata
                index[vector_id] = {}
                for existing_id, existing_vector in vector_data.items():
                    if existing_id != vector_id:
                        similarity = self._calculate_similarity(vector, existing_vector, self.space)
                        index[vector_id][existing_id] = similarity
                        index[existing_id][vector_id] = similarity

    def update_vector(self, store_id: int, vector_id: int, vector: list[float], metadata: dict = None):
        if store_id in self.vector_stores:
            vector_data = self.vector_stores[store_id]['vector_data']
            index = self.vector_stores[store_id]['vector_index']
            metadata_store = self.vector_stores[store_id]['metadata']
            if vector_id in vector_data:
                vector_data[vector_id] = vector
                if metadata:
                    metadata_store[vector_id] = metadata
                for existing_id, existing_vector in vector_data.items():
                    if existing_id != vector_id:
                        similarity = self._calculate_similarity(vector, existing_vector, self.space)
                        index[vector_id][existing_id] = similarity
                        index[existing_id][vector_id] = similarity
    
    def find_similar_vectors(self, store_id: int, query_vector: list[float], num_results: int = 5, metadata_filter: dict = None, space: str = 'cosine'):
        if store_id in self.vector_stores:
            vector_data = self.vector_stores[store_id]['vector_data']
            metadata = self.vector_stores[store_id]['metadata']
            similarities = []

            for vector_id, vector in vector_data.items():
                if len(query_vector) != len(vector):
                    raise StackAIError("Query vector length does not match the length of the chunk embeddings.", error_code=400)
                
                if metadata_filter:
                    if not self._metadata_matches(metadata[vector_id], metadata_filter):
                        continue
                similarity = self._calculate_similarity(query_vector, vector, space)
                similarities.append((vector_id, similarity))
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:num_results]    
