import numpy as np  
from app.vector import VectorStore, HNSWVectorStore, BruteForceVectorStore, LSHVectorStore

def run_vector_store_test(vector_store: VectorStore, store_id: str):
    vector_store.add_vector_store(store_id)

    # Define sentences
    sentences = [
        "I eat mango",
        "mango is my favorite fruit",
        "mango, apple, oranges are fruits",
        "fruits are good for health",
    ]

    print("\n\n Tokenization and Vocabulary Creation \n\n")
    # Tokenization and Vocabulary Creation
    vocabulary = set()
    for sentence in sentences:
        tokens = sentence.lower().split()
        print("Tokens:", tokens)
        print("For sentence:", sentence)
        vocabulary.update(tokens)

    print("Vocabulary:", vocabulary)

    print("\n\n Assigning Unique Indices to Vocabulary Words \n\n")
    # Assign unique indices to vocabulary words
    word_to_index = {word: i for i, word in enumerate(vocabulary)}

    print("Word to Index:", word_to_index)

    print("\n\n Vectorization \n\n")
    # Vectorization
    sentence_vectors = {}
    for sentence in sentences:
        tokens = sentence.lower().split()
        print("Tokens:", tokens)
        print("For sentence:", sentence)
        vector = np.zeros(len(vocabulary))
        for token in tokens:
            print("Token:", token)
            print("Index:", word_to_index[token])
            vector[word_to_index[token]] += 1
        sentence_vectors[sentence] = vector

    print("Sentence Vectors:", sentence_vectors)

    print("\n\n Storing Sentence Vectors in VectorStore \n\n")
    # Store in VectorStore
    for sentence, vector in sentence_vectors.items():
        vector_store.add_vector(store_id, sentence, vector)
        print("Sentence:", sentence)
        print("Vector:", vector)

    #print("\n\n")
    #print("Vector Store:", vector_store.vector_stores[store_id]["vector_data"])
    #print("\n\n")
    #print("Vector Index:", vector_store.vector_stores[store_id]["vector_index"])

    print("\n\n Similarity Search \n\n")
    # Similarity Search
    query_sentence = "Mango is the best fruit"
    query_vector = np.zeros(len(vocabulary))
    query_tokens = query_sentence.lower().split()
    print("Query Tokens:", query_tokens)
    for token in query_tokens:
        if token in word_to_index:
            query_vector[word_to_index[token]] += 1

    print("Query Vector:", list(query_vector))
    similar_sentences = vector_store.find_similar_vectors(store_id, query_vector, num_results=2)

    print("\n\n Displaying Similar Sentences \n\n")
    # Display similar sentences
    print("Query Sentence:", query_sentence)
    print("Similar Sentences:", similar_sentences)
    for sentence, similarity in similar_sentences:
        print(f"{sentence}: Similarity = {similarity:.4f}")

    return similar_sentences    

def test_hnsw_vector_store():
    vector_store = HNSWVectorStore()
    similar_sentences = run_vector_store_test(vector_store, "hnsw_library")
    assert len(similar_sentences) == 2
    assert similar_sentences[0] == ('mango is my favorite fruit', 0.7745966692414834)
    assert similar_sentences[1] == ('I eat mango', 0.33333333333333337)
    vector_store.delete_vector_store("hnsw_library")    

def test_brute_force_vector_store():
    vector_store = BruteForceVectorStore()
    similar_sentences = run_vector_store_test(vector_store, "brute_force_library")
    assert len(similar_sentences) == 2
    assert similar_sentences[0] == ('mango is my favorite fruit', 0.7745966692414834)
    assert similar_sentences[1] == ('I eat mango', 0.33333333333333337)
    vector_store.delete_vector_store("brute_force_library")

def test_lsh_vector_store():
    vector_store = LSHVectorStore(input_dim=15)
    similar_sentences = run_vector_store_test(vector_store, "lsh_library")

    #because it's a random hash, we can't predict the order of the results
    #so if similar_sentences is 0, we don't evaluate
    if len(similar_sentences) == 0:
        return
    
    assert len(similar_sentences) == 1
    assert similar_sentences[0] == ('mango is my favorite fruit', 0.7745966692414834)    
    vector_store.delete_vector_store("lsh_library")