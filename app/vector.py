import numpy as np
from abc import ABC, abstractmethod
from app.models import StackAIError

class VectorStore(ABC):   
    def __init__(self):
        self.vector_stores = {}

    @abstractmethod
    def add_vector_store(self, store_id: int):
        """
        Add a new vector store with the given store_id.
        
        :param store_id: Unique identifier for the vector store.
        """
        pass

    @abstractmethod
    def add_vector(self, store_id: int, vector_id: int, vector: list[float], metadata: dict = None):
        """
        Add a vector to the specified vector store.
        
        :param store_id: Unique identifier for the vector store.
        :param vector_id: Unique identifier for the vector.
        :param vector: List of floats representing the vector.
        :param metadata: Dictionary of metadata associated with the vector.
        """
        pass

    @abstractmethod
    def update_vector(self, store_id: int, vector_id: int, new_vector: list[float], metadata: dict = None):
        """
        Update an existing vector in the specified vector store.
        
        :param store_id: Unique identifier for the vector store.
        :param vector_id: Unique identifier for the vector.
        :param new_vector: List of floats representing the new vector.
        :param metadata: Dictionary of metadata associated with the vector (optional).
        """
        pass

    @abstractmethod
    def get_vector(self, store_id: int, vector_id: int):
        """
        Retrieve a vector from the specified vector store.
        
        :param store_id: Unique identifier for the vector store.
        :param vector_id: Unique identifier for the vector.
        :return: The vector corresponding to the given vector_id.
        """
        pass

    @abstractmethod
    def find_similar_vectors(self, store_id: int, query_vector: list[float], num_results: int, metadata_filter: dict = None):
        """
        Find vectors similar to the query vector in the specified vector store.
        
        :param store_id: Unique identifier for the vector store.
        :param query_vector: List of floats representing the query vector.
        :param num_results: Number of similar vectors to return.
        :param metadata_filter: Dictionary of metadata filters to apply (optional).
        :return: List of tuples containing vector_id and similarity score.
        """
        pass
    
    @abstractmethod
    def delete_vector_store(self, store_id: int):
        """
        Delete the specified vector store.
        
        :param store_id: Unique identifier for the vector store.
        """
        pass
    
    def _value_matches(self, metadata_value, filter_value) -> bool:
        if isinstance(filter_value, (str, int, float)):
            return metadata_value == filter_value
        elif isinstance(filter_value, dict):
            operators = {
                "$gte": lambda a, b: a >= b,
                "$gt": lambda a, b: a > b,
                "$lte": lambda a, b: a <= b,
                "$lt": lambda a, b: a < b,
                "$eq": lambda a, b: a == b,
                "$ne": lambda a, b: a != b
            }
            for op, val in filter_value.items():
                if op in operators and not operators[op](metadata_value, val):
                    return False
            return True
        return False

    def _metadata_matches(self, vector_metadata: dict, metadata_filter: dict) -> bool:
        for key, value in metadata_filter.items():
            if key not in vector_metadata or not self._value_matches(vector_metadata[key], value):
                return False
        return True

    def _calculate_similarity(self, vector1: list[float], vector2: list[float], space: str = 'cosine') -> float:
        if space == 'cosine':
            return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        elif space == 'l2':
            return -np.linalg.norm(np.array(vector1) - np.array(vector2))
        else:
            raise ValueError("Unsupported space type")


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

    def find_similar_vectors(self, store_id: int, query_vector: list[float], num_results: int = 5, metadata_filter: dict = None):
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
                similarity = self._calculate_similarity(query_vector, vector)
                similarities.append((vector_id, similarity))
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:num_results]


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

    def find_similar_vectors(self, store_id: int, query_vector: list[float], num_results: int = 5, metadata_filter: dict = None):
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
                similarity = self._calculate_similarity(query_vector, vector, self.space)
                similarities.append((vector_id, similarity))
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:num_results]