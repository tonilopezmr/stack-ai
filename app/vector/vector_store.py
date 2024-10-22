import numpy as np
from abc import ABC, abstractmethod
from app.models import Document, Library

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
    def delete_vector_store(self, store_id: int):
        """
        Delete the specified vector store.
        
        :param store_id: Unique identifier for the vector store.
        """
        pass

    @abstractmethod
    def delete_vector(self, store_id: int, vector_id: int):
        """
        Delete a vector from the specified vector store.
        
        :param store_id: Unique identifier for the vector store.
        :param vector_id: Unique identifier for the vector.
        """
        pass
    
    @abstractmethod
    def find_similar_vectors(self, store_id: int, query_vector: list[float], num_results: int = 5, metadata_filter: dict = None, space: str = 'cosine') -> list[float]:
        """
        Find vectors similar to the query vector in the specified vector store.

        The metadata_filter allows you to specify conditions that the metadata of the vectors must meet.
        The filter can be a simple equality check or can use comparison operators for more complex queries.
        
        Available comparison operators:
        - $eq: Equal to
        - $ne: Not equal to
        - $gt: Greater than
        - $gte: Greater than or equal to
        - $lt: Less than
        - $lte: Less than or equal to

        Examples:
        - {'author': 'Author 1'} will filter vectors whose metadata has an 'author' field equal to 'Author 1'.
        - {'timestamp': {'$gte': 1672531199000}} will filter vectors with a 'timestamp' field greater than or equal to 1672531199000.

        :param store_id: Unique identifier for the vector store.
        :param query_vector: List of floats representing the query vector.
        :param num_results: Number of similar vectors to return (default is 5).
        :param metadata_filter: Dictionary of metadata to filter the vectors (optional).
        :param space: The space in which to calculate similarity ('cosine' or 'l2', default is 'cosine').
        :return: A list of tuples containing the vector_id and similarity score of the most similar vectors.
        """
        pass

    def vector_store_exists(self, store_id: int) -> bool:
        """
        Check if a vector store with the given store_id exists.
        
        :param store_id: Unique identifier for the vector store.
        :return: True if the vector store exists, False otherwise.
        """
        return store_id in self.vector_stores    
       
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

    def _has_chunks(self, document: Document) -> bool:
        return len(document.chunks) > 0
    
    def add_library_chunks_if_needed(self, library: Library):
        """
        Add vectors of a library document's chunks to the vector store.

        Args:
            library_id (int): The identifier of the library.
            document (Document): The document containing chunks with vectors.
        """
        for document in library.documents:            
            if self._has_chunks(document):
                for chunk in document.chunks:
                    self.add_vector(library.id, chunk.id, chunk.embedding, chunk.metadata)
    
    def add_document_chunks_if_needed(self, library_id: int, document: Document):
        """
        Add vectors of a document's chunks to the vector store.

        Args:
            library_id (int): The identifier of the library.
            document (Document): The document containing chunks with vectors.
        """
        if self._has_chunks(document):
            for chunk in document.chunks:
                self.add_vector(library_id, chunk.id, chunk.embedding, chunk.metadata)

