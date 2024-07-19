from app.routers.libraries import create_library, read_library, delete_library
from app.routers.chunks import create_chunk, read_chunk
from app.models import Chunk, Document, Library
import pytest
from fastapi import HTTPException

def get_dummy_library():         
    chunk1 = Chunk(
        id=1,
        text="Chunk 1 text",
        embedding=[0.1, 0.2, 0.3],
        metadata={"author": "Author 1", "date": "2024-01-01"}
    )

    chunk2 = Chunk(
        id=2,
        text="Chunk 2 text",
        embedding=[0.4, 0.5, 0.6],
        metadata={"author": "Author 2", "date": "2024-01-02"}
    )

    chunk3 = Chunk(
        id=3,
        text="Chunk 3 text",
        embedding=[0.7, 0.8, 0.9],
        metadata={"author": "Author 3", "date": "2024-01-03"}
    )
    
    document1 = Document(
        id=1,
        chunks=[chunk1, chunk2],
        metadata={"title": "Document 1", "category": "Category A"}
    )

    document2 = Document(
        id=2,
        chunks=[chunk3],
        metadata={"title": "Document 2", "category": "Category B"}
    )
    
    dummy_library = Library(
        id=1,
        documents=[document1, document2],
        metadata={"library_name": "Example Library", "location": "Location X"}
    )

    return dummy_library

def setup_function(function):
    library = get_dummy_library()
    delete_library(library.id)

def test_create_library():
    library = get_dummy_library()
    
    new_library = create_library(library)

    result_library = read_library(library.id)
    assert new_library.id == result_library.id    


def test_read_library():
    library = get_dummy_library()
    create_library(library)
    
    result_library = read_library(library.id)
    assert result_library.id == library.id
    assert result_library.metadata == library.metadata

def test_delete_library():
    library = get_dummy_library()
    create_library(library)
    
    delete_library(library.id)
    
    with pytest.raises(HTTPException) as excinfo:
        read_library(library.id)
    assert excinfo.value.status_code == 404

def test_create_chunk():
    library = get_dummy_library()
    new_library = create_library(library)
    assert new_library is not None
    
    document_id = library.documents[0].id
    new_chunk = Chunk(
        id=3,
        text="New chunk text",
        embedding=[0.1, 0.2, 0.3],
        metadata={"author": "New Author", "date": "2024-01-04"}
    )
    
    created_chunk = create_chunk(library.id, document_id, new_chunk)
    assert created_chunk is not None
    
    result_chunk = read_chunk(library.id, new_chunk.id)    
    assert result_chunk.text == new_chunk.text

def test_read_chunk():
    library = get_dummy_library()
    create_library(library)
        
    chunk_id = library.documents[0].chunks[0].id
    
    result_chunk = read_chunk(library.id, chunk_id)
    assert result_chunk.id == chunk_id
    assert result_chunk.text == library.documents[0].chunks[0].text