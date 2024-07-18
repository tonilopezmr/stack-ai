from app.vector.vector_store import VectorStore

class BruteForceVectorStore(VectorStore):    
    def __init__(self):
        super().__init__()

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
            
    def add_vector(self, store_id: int, vector_id: int, vector: list[float], metadata: dict = None):
        if store_id in self.vector_stores:
            self.vector_stores[store_id]['vector_data'][vector_id] = vector
            if metadata:
                self.vector_stores[store_id]['metadata'][vector_id] = metadata
            self._update_index(store_id, vector_id, vector)

    def update_vector(self, store_id: int, vector_id: int, new_vector: list[float], metadata: dict = None):
        if store_id in self.vector_stores and vector_id in self.vector_stores[store_id]['vector_data']:
            self.vector_stores[store_id]['vector_data'][vector_id] = new_vector
            if metadata:
                self.vector_stores[store_id]['metadata'][vector_id] = metadata
            self._update_index(store_id, vector_id, new_vector)

    def get_vector(self, store_id: int, vector_id: int):
        if store_id in self.vector_stores:
            return self.vector_stores[store_id]['vector_data'].get(vector_id)

    def _update_index(self, store_id: int, vector_id: int, vector: list[float]):
        if store_id in self.vector_stores:
            vector_data = self.vector_stores[store_id]['vector_data']
            vector_index = self.vector_stores[store_id]['vector_index']
            for existing_id, existing_vector in vector_data.items():
                similarity = self._calculate_similarity(vector, existing_vector)
                if existing_id not in vector_index:
                    vector_index[existing_id] = {}
                vector_index[existing_id][vector_id] = similarity
