# Stack AI Exercise

In this repository, you will find the [Stack AI exercise](https://github.com/tonilopezmr/stack-ai/blob/main/EXERCISE.md) solution by [@tonilopezmr](https://www.tonilopezmr.com/)

:warning: Important: Please read this document to understand the decisions that were made.

You follow the implementation process following each PR:

* [Init project, routers, simple services and in memory storage PR#1](https://github.com/tonilopezmr/stack-ai/pull/1)
* [Add Vector DB with different implementations brute force and HNSW indexing algorithm, and search query including metadata PR#2](https://github.com/tonilopezmr/stack-ai/pull/2)
* [Uses Vector store as in memory caches making sure data will be available PR#3](https://github.com/tonilopezmr/stack-ai/pull/3)
* [Include postgress datasource #4](https://github.com/tonilopezmr/stack-ai/pull/4)
* [Include heml k8s files to run the service using k8 #5](https://github.com/tonilopezmr/stack-ai/pull/5)


<br/>

  
### Project Structure

* `app`: The Fast API application
    * `routes`: Contains the API endpoints
    * `services`: Manages the orchestration of different data sources or core business logic. The architecture focuses on simplicity, emphasizing the VectorStore and Data Sources.
    * `storage`: The storage layer, supporting various data sources such as in-memory, SQL. You can easily add NoSQL, or other sources like Redis.
    * `vector`: Contains a custom in-memory Vector Database for storing chunk vectors.
* `tests`: Some tests I wrote for learning vector indexing, data sources orchestration, and routes
     * `units`: They pretend to be unit tests without external configurations
     * `integration`: I test the routes and end-to-end solution up to in-memory database (don't use Postgres for testing)
* `stack-ai`: [Helm project](https://helm.sh/) files


 
I have decided to expose only two options, libraries that contain documents and chunks that are associated with a document, in this way, I keep the code simple.
I don't handle any Documents, they are created with Libraries and you can add or remove chunks to a document. That's why there aren't routes for `documents` and no classes for managing documents as the library is responsible for doing that.

<br/>

### Routes API Endpoints

:accessibility: You can use [client.http file](https://github.com/tonilopezmr/stack-ai/blob/main/client.http) with the [REST Client VSCode](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) extension: humao.rest-client, *calling to the endpoints easily clicking to the curl buttons.* 

<img width="1414" alt="Screenshot 2024-07-19 at 20 18 48" src="https://github.com/user-attachments/assets/a54add0a-0a1f-4e42-a61b-c563ec98a8d0">

How a Library looks like:

```json
{
  "id": 1,
  "documents": [
    {
      "id": 1,
      "chunks": [
        {
          "id": 1,
          "text": "Chunk 1 text",
          "metadata": {"author": "Author 1", "date": "2024-01-01"},
          "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
      ],
      "metadata": {"title": "Document 1", "category": "Category A"}
    },
    {
      "id": 2,
      "chunks": [
        {
          "id": 3,
          "text": "Chunk 3 text",
          "metadata": {"author": "Author 3", "date": "2024-01-03"},
          "embedding": [1.1, 1.2, 1.3, 1.4, 1.5]
        }
      ],
      "metadata": {"title": "Document 2", "category": "Category B"}
    }
  ],
  "metadata": {"library_name": "Example Library", "location": "Location X"}
}
```

<br/>

### Services

API Endpoints are the entry points for the customer which calls to the Services which are the entry points to our core business.

Service responsibility is to make each action of our business, in this case, orchestrates the different data sources to stay in sync and calls to the vector store to perform operations.

For example, creating a library consists of saving the library on a persistent database and indexing the chunks to the vector store. 

```python
def create(self, library: Library):
        """
        Create a new library and add the chunks of the documents to the vector store.
        """
        new_library = self.libraries.add(library)
        self.vector_store.add_vector_store(new_library.id)

        self.vector_store.add_library_chunks_if_needed(new_library)
            
        return new_library
```

<br/>

### Storage

There are two different implementations for storing information, In-Memory and Postgres, which extend from `LibraryDataSource` (or chunk).

This makes the change of data sources very easy and quick using the `D` from `SOLID`, Dependency injection:

```
#This could go in a DataSourceFactory class, to make it simple is like this
if DATASOURCE == IN_MEMORY_DATASOURCE_OPTION: 
    library_datasource = LibraryInMemoryDatasource()    
else:
    connection_pool = initialize_postgresql()        
    library_datasource = LibraryPostgresDatasource(chunk_datasource, connection_pool)

library_service = LibraryService(library_datasource) # LibraryService don't know which implementation is going to be used
```

You can see the full configuration [app/routes/__init__.py](https://github.com/tonilopezmr/stack-ai/blob/main/app/routers/__init__.py)

#### Data Races

Each data source is responsible for making sure there are not going to be concurrent data races, for in-memory implementation I used `Thread.lock` which is the simplest way to do it, and used transactions on SQL using a Connection Pool (`pool.SimpleConnectionPool`).

Locking is not the most efficient way to do it as It can make our services slow with big volumes, for It will require the use of a better `ThreadPoolExecutor` implementation for better performance.

[Disk persistence using postgres is part of PR#4](https://github.com/tonilopezmr/stack-ai/pull/4)

<br/>

### VectorStore

#### Database

I wanted to focus on learning the indexing problems and I wanted to keep it simple, on storing the vectors and not managing documents, from a Vector perspective a `library` is a list of `chunks`.
This vector store uses in-memory storage for storing all the vector's information and acts as a cache between `LibraryDataSource` which is a slower storage option.

If we would like to scale the Vector Storage to store big loads, a nice option is to use Redis, so the read/writes will be faster.

#### Algorithms

I'm not an expert in this field but I have been working with different Vector Databases and different algorithms in IBM Research AI department, It was fun to learn about it and I tried my best to implement the solutions, however, there's a high probability are not well coded.

I believe there are some issues with the metadata, as you advised against using a free metadata schema, which I did. It would be helpful to discuss this and have you show me the correct way to use metadata.

* Brute Force (Flat)
* Locality-Sensitive Hashing (LSH)
* Hierarchical Navigable Small World (HNSW)

#### Brute Force

<img width="400" alt="Brute Force" src="https://miro.medium.com/v2/resize:fit:1400/format:webp/0*8df_OfoywQ3fmd_w.png">

[Brute Force source](https://medium.com/@vipra_singh/building-llm-applications-vector-database-part-4-2bb29e7c798d#97d2)

This is a very good option if we aim for big quality on smaller datasets because the quality is 100% but it uses a lot of memory and for larger datasets is slow as well.

I have learned vector indexing and similarity search using Brute force, I still have some questions as I believe I didn't do the correct implementation.

#### Locality-Sensitive Hashing (LSH)

<img width="400" alt="LSH" src="https://miro.medium.com/v2/resize:fit:1400/format:webp/0*T0X7CSzV0kqjf2Fe.png">

[LSH source](https://medium.com/@vipra_singh/building-llm-applications-vector-database-part-4-2bb29e7c798d#a352)

Not really an option to use it, It was a nice exercise to learn about it.
This one is a bit random as It generates the random hash table and sometimes doesn't find the solution, I'm wondering if that's why his quality is that bad.

#### Hierarchical Navigable Small World (HNSW)

<img width="400" alt="HNSW" src="https://miro.medium.com/v2/resize:fit:1400/format:webp/0*xbcbNvitjC-XO6LB.png">

[HNSW full explanation](https://www.pinecone.io/learn/series/faiss/hnsw/)

This is one of the better solutions and why most of the Vector databases use this algorithm, great quality, super fast and It uses little memory.

I guess I didn't implement it 100% well, It seems it works with the tests I have done, and for sure the most complicated one to implement, I have done it with the help of [hnsw-python](https://github.com/RyanLiGod/hnsw-python) implementation and a great library open source called [hnswlib](https://github.com/nmslib/hnswlib).


#### VectorStore implementation

Following the same way as `DataSources`, there is a parent `VectorStore` for common work with the different implementations, so It's easy to change the `VectorStore` algorithm using Dependency inversion.

```
brute_force = BruteForceVectorStore()
hnsw = HNSWVectorStore()
lsh = LSHVectorStore()

vector_service = VectorService(hnsw)
```

You can see the full configuration [app/routes/__init__.py](https://github.com/tonilopezmr/stack-ai/blob/main/app/routers/__init__.py)

<br/>

### Vector Search

Vector Search has three arguments, `vector_query`, `num_results` (k), and `filter_metadata`.

Each algorithm handles the search request differently. 

If the vector for some reason is not found on the vector database, It will check if it's in the database to search the library. As VectorStore acts as a cache, so the first search if it's not previously loaded the information, It will be slower, but then the rest will be way faster. (I explain here this because search function doesn't call the database directly to bring information, only if it's needed, the rest should be in already loaded in the VectorStore)

```
curl -X POST "http://localhost:8080/libraries/15/search_vectors" -H "Content-Type: application/json" -d '{
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
  "num_results": 2,
  "filter_metadata": {"author": "Author 1"}
}'
```

#### Metadata Filtering

The metadata_filter allows you to specify conditions that the metadata of the vectors must meet. The filter can be a simple equality check or can use comparison operators for more complex queries.

Available comparison operators:
```
$eq: Equal to
$ne: Not equal to
$gt: Greater than
$gte: Greater than or equal to
$lt: Less than
$lte: Less than or equal to
```

Examples:

```
{'author': 'Author 1'} will filter vectors whose metadata has an 'author' field equal to 'Author 1'.
{'timestamp': {'$gte': 1672531199000}} will filter vectors with a 'timestamp' field greater than or equal to 1672531199000.
```

[VectorStore is part of PR#2, you can read more about it here](https://github.com/tonilopezmr/stack-ai/pull/2)

<br/>

### Kubernetes

I have created a [Helm project](https://helm.sh/) to be able to run the exercise in kubernetes if you want. The simplest solution for working on localhost would be using `docker-compose` and runnign the app using uvicorn.

This consists of a Postgres service and the Python service, the way to access the python app is through a port-forward, I didn't have time to do a different setup, like `LoadBalancer` or any other option like `NodePort`.

[Full explanation on how to run the kubernetes cluster, on the PR#5](https://github.com/tonilopezmr/stack-ai/pull/5)

Another option is to run docker-compose and uvicorn:

```shell
export DATASOURCE=postgres

docker-compose up -d
uvicorn app.main:app --reload --port 8080 # don't need a database by default
```

[Kubernetes is part of PR#5, you can read more](https://github.com/tonilopezmr/stack-ai/pull/5)

## Setting up the Environment

**Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate 
    ```

**Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to run

By default, it doesn't use any external database. 
⚠️ If you don't use any external database, the ID's aren't autogenerated

```bash
uvicorn app.main:app --reload
```
