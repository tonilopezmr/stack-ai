# Take-at-Home Task - Backend Engineer (Vector DB)

Congrats on making it thus far in the interview process!
Here is a 4-day task for you to show us where you shine the most 🙂

## Objective

The goal of this project is to develop a REST API that allows users to index and query their documents within a Vector Database. A Vector Database specializes in storing and indexing vector embeddings, enabling fast retrieval and similarity searches. This capability is crucial for applications involving natural language processing, recommendation systems, and more.

The REST API should be containerized in a Docker container and deployed in a standalone Kubernetes cluster (no need to have more than one db node).

### Definitions

To ensure a clear understanding, let's define some key concepts:

1. Chunk: A chunk is a piece of text with an associated embedding and metadata.
2. Document: A document is made out of multiple chunks, it also contains metadata.
3. Library: A library is made out of a list of documents and can also contain other metadata.

The API should:

1. Allow the users to create, read, update, and delete libraries.
2. Allow the users to create, read, update and delete chunks within a library.
3. Index the contents of a library.
4. Do k-Nearest Neighbor vector search over the selected library with a given embedding query.

### Guidelines:

Even though it is not the best language for the job, the project should be written in Python since that is what we use to develop our backend.

Here is a suggested path on how to implement a basic solution to the problem.

1. Define the Chunk, Document and Library classes. To simplify schema definition, we suggest you use a fixed schema for each of the classes. This means not letting the user define which fields should be present within the metadata for each class. Following this path you will have fewer problems validating insertions/updates, but feel to let the users define their own schemas for each library if you are up for the challenge.
2. Implement two or three indexing algorithms, do not use external libraries, we want to see you code them up. What is the space and time complexity for each of the indexes? Why did you choose this index?
3. Implement the necessary data structures/algorithms to ensure that there are no data races between reads and writes to the database. Explain your design choices.
4. Create the logic to do the CRUD operations on libraries and documents/chunks. Ensure data consistency and integrity during these operations.
5. Implement an API layer on top of that logic to let users interact with the vector database.
6. Create a docker image for the project and a helmchart to install it in a kubernetes cluster like minikube. 

### Extra Points:

Here are some additional suggestions on how to enhance the project even further. You are not required to implement any of these, but if you do, we will value it. If you have other improvements in mind, please feel free to implement them and document them in the project’s README file.

1. **Python SDK Client**:
    - Develop a Python SDK client that interfaces with your API, making it easier for users to interact with the vector database programmatically. This client should include comprehensive documentation and examples.
2. **Metadata filtering:**
    - Add the possibility of using metadata filters to enhance query results: ie: do kNN search over all chunks created after a given date, whose name contains xyz string etc etc.
3. **Persistence to Disk**:
    - Implement a mechanism to persist the database state to disk, ensuring that the docker container can be restarted and resume its operation from the last savepoint. Explain your design choices and tradeoffs, considering factors like performance, consistency, and durability.
4. **Leader-Follower Architecture**:
    - Design and implement a leader-follower (master-slave) architecture to support multiple database nodes within the Kubernetes cluster. This architecture should handle read scalability and provide high availability. Explain how leader election, data replication, and failover are managed, along with the benefits and tradeoffs of this approach.

## Constraints

Do **not** use libraries like chroma-db, pinecone, FAISS, etc to develop the project, we want to see you write the algorithms yourself.

You may use llama-index or any other library to help you parse, chunk and embed some documents to test your system. We will not be grading you on the quality of the chunking/embedding, so don’t spend too much time doing this.

## **Tech Stack**

- **API Backend:** Python + Fast-API + Pydantic

## Resources:

[Cohere](https://cohere.com/embeddings) API key to create the embeddings for your test.

```markdown
********************
```

## Evaluation Criteria

We will evaluate the code functionality and its quality.

**Code quality:**

- [SOLID design principles](https://medium.com/byborg-engineering/applying-solid-to-react-ca6d1ff926a4).
- Use of static typing.
- FastAPI good practices.
- Code modularity and reusability.
- Use of RESTful API endpoints.
- Project containerization with Docker.
- Testing
- Error handling.

**Functionality:**

- Does everything work as expected?

## Deliverable

1. **Source Code**: A link to a GitHub repository containing all your source code.
2. **Documentation**: A README file that documents the task, explains your technical choices, how to run the project locally, and any other relevant information.
3. **Demo video:**
    1. A screen recording where you show how to install the project and interact with it in real time.
    2. A screen recording of your design with an explanation of your design choices and thoughts/problem-solving.

## Timeline

You have **4 days** (96h) from the receipt of this test to submit your deliverables 🚀

## Questions

Feel free to reach out at any given time with questions about the task, particularly if you encounter problems outside your control that may block your progress.