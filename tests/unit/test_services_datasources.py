"""Behaviour tests to ensure the services orchestration between dataservices is working fine"""

import pytest
from unittest.mock import MagicMock
from app.services.chunk_service import ChunkService
from app.services.library_service import LibraryService
from app.services.vector_service import VectorService
from app.models import Chunk, Library, QueryVector

@pytest.fixture
def setup_services():
    chunk_datasource = MagicMock()
    library_datasource = MagicMock()
    vector_store = MagicMock()

    chunk_service = ChunkService(chunk_datasource, vector_store)
    library_service = LibraryService(library_datasource, vector_store)
    vector_service = VectorService(library_datasource, chunk_datasource, vector_store)

    return chunk_service, library_service, vector_service, chunk_datasource, library_datasource, vector_store

def test_chunk_service_create(setup_services):
    chunk_service, _, _, chunk_datasource, _, vector_store = setup_services
    chunk = Chunk(id=1, text="Test chunk", embedding=[0.1, 0.2, 0.3], metadata={"author": "Author 1"})
    chunk_datasource.add.return_value = chunk

    result = chunk_service.create(1, 1, chunk)

    chunk_datasource.add.assert_called_once_with(1, 1, chunk)
    vector_store.add_vector.assert_called_once_with(1, 1, chunk.embedding, chunk.metadata)
    assert result == chunk

def test_library_service_create(setup_services):
    _, library_service, _, _, library_datasource, vector_store = setup_services
    library = Library(id=1, documents=[], metadata={"name": "Test Library"})
    library_datasource.add.return_value = library

    result = library_service.create(library)

    library_datasource.add.assert_called_once_with(library)
    vector_store.add_vector_store.assert_called_once_with(1)
    vector_store.add_library_chunks_if_needed.assert_called_once_with(library)
    assert result == library

def test_vector_service_search_similar_sentences(setup_services):
    _, _, vector_service, chunk_datasource, _, vector_store = setup_services
    query_vector = QueryVector(vector=[0.1, 0.2, 0.3], num_results=2, filter_metadata={"author": "Author 1"})
    vector_store.vector_store_exists.return_value = True
    vector_store.find_similar_vectors.return_value = [(1, 0.9), (2, 0.8)]
    chunk = Chunk(id=1, text="Test chunk", embedding=[0.1, 0.2, 0.3], metadata={"author": "Author 1"})
    chunk_datasource.get.return_value = chunk

    result = vector_service.search_similar_sentences(1, query_vector)

    vector_store.vector_store_exists.assert_called_once_with(1)
    vector_store.find_similar_vectors.assert_called_once_with(1, query_vector.vector, query_vector.num_results, query_vector.filter_metadata)
    chunk_datasource.get.assert_called_with(1, 1)
    assert result == [("Test chunk", 0.9)]