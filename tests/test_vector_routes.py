import pytest
from app.routers.vector import router as vector_router
from app.routers.libraries import router as library_router
from app.models import Chunk, Document, Library
import numpy as np
from app.routers.libraries import create_library
from app.routers.vector import search_vector_similarities, QueryVector

def get_dummy_library():             
    chunk1 = Chunk(
        id=1,
        text="I eat mango",
        embedding=[0.1, 0.2, 0.3],
        metadata={"author": "Author 1", "date": 1704067200000}
    )

    chunk2 = Chunk(
        id=2,
        text="mango is my favorite fruit",
        embedding=[0.4, 0.5, 0.6],
        metadata={"author": "Author 2", "date": 1704067200010}
    )

    chunk3 = Chunk(
        id=3,
        text="mango, apple, oranges are fruits",
        embedding=[0.7, 0.8, 0.9],
        metadata={"author": "Author 2", "date": 1704067200020}
    )
    
    chunk4 = Chunk(
        id=4,
        text="fruits are good for health",
        embedding=[1.0, 1.1, 1.2],
        metadata={"author": "Author 1", "date": 1704067200040}
    )

    vocabulary = set()
    for sentence in [chunk1, chunk2, chunk3, chunk4]:
        tokens = sentence.text.lower().split()
        vocabulary.update(tokens)

    vocabulary = sorted(vocabulary)  # Sorting the vocabulary to have a consistent order

    word_to_index = {word: i for i, word in enumerate(vocabulary)}
    
    for sentence in [chunk1, chunk2, chunk3, chunk4]:
        tokens = sentence.text.lower().split()
        vector = np.zeros(len(vocabulary))
        for token in tokens:
            vector[word_to_index[token]] += 1
        sentence.embedding = list(vector)           

    document1 = Document(
        id=1,
        chunks=[chunk1, chunk2, chunk3, chunk4],
        metadata={"title": "Document 1", "category": "Category A"}
    )
    
    dummy_library = Library(
        id=2,
        documents=[document1],
        metadata={"library_name": "Example Library", "location": "Location X"}
    )    

    return dummy_library


def test_search_vector_similarities():
    library = get_dummy_library()
    
    # Create library
    create_library(library)    

    # Perform similarity search for "Mango is the best fruit"    
    query_vector = QueryVector(
        num_results=2,
        vector=[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0]
    )
    
    similar_sentences = search_vector_similarities(library.id, query_vector)        

    assert len(similar_sentences) == 2
    assert similar_sentences[0] == ('mango is my favorite fruit', 0.7745966692414834)
    assert similar_sentences[1] == ('I eat mango', 0.33333333333333337)

def test_search_vector_similarities_with_metadata_filter_author_1():
    library = get_dummy_library()
    
    # Create library
    create_library(library)    

    # Perform similarity search for "Mango is the best fruit"    
    query_vector = QueryVector(
        num_results=2,
        vector=[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
        filter_metadata={"author": "Author 1"}
    )
    
    similar_sentences = search_vector_similarities(library.id, query_vector)        

    assert len(similar_sentences) == 2
    assert similar_sentences[0] == ('I eat mango', 0.33333333333333337)
    assert similar_sentences[1] == ('fruits are good for health', 0.0)

def test_search_vector_similarities_with_metadata_filter_date_after_1704067200010():
    library = get_dummy_library()
    
    # Create library
    create_library(library)    

    # Perform similarity search for "Mango is the best fruit"    
    query_vector = QueryVector(
        num_results=2,
        vector=[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
        filter_metadata={"date": {"$gte": 1704067200010}}
    )
    
    similar_sentences = search_vector_similarities(library.id, query_vector)        

    assert len(similar_sentences) == 2
    assert similar_sentences[0] == ('mango is my favorite fruit', 0.7745966692414834)
    assert similar_sentences[1] == ('mango, apple, oranges are fruits', 0.0)
