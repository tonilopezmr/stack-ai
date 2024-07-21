from app.services import ChunkService, LibraryService, VectorService, DocumentService
from app.storage import ChunkInMemoryDatasource, LibraryInMemoryDatasource, ChunkPostgresDatasource, LibraryPostgresDatasource, DocumentInMemoryDatasource, DocumentPostgresDatasource
from app.vector import BruteForceVectorStore, HNSWVectorStore
import os
from app.storage.sql_datasource.config import initialize_postgresql

POSTGRES_DATASOURCE_OPTION = 'postgres'
IN_MEMORY_DATASOURCE_OPTION = 'in-memory'
DATASOURCE = os.getenv('DATASOURCE', IN_MEMORY_DATASOURCE_OPTION)  # Default to 'in-memory' if not set, options: postgres or in-memory
print("Datasource selected: ", DATASOURCE)

library_datasource = None
chunk_datasource = None
document_datasource = None

if DATASOURCE == IN_MEMORY_DATASOURCE_OPTION:
    library_datasource = LibraryInMemoryDatasource()
    chunk_datasource = ChunkInMemoryDatasource(library_datasource)
    document_datasource = DocumentInMemoryDatasource(library_datasource)
else:
    connection_pool = initialize_postgresql()    
    chunk_datasource = ChunkPostgresDatasource(connection_pool)
    library_datasource = LibraryPostgresDatasource(chunk_datasource, connection_pool)
    document_datasource = DocumentPostgresDatasource(chunk_datasource, connection_pool)

hnsw_vector = HNSWVectorStore()
vector_store = BruteForceVectorStore()

library_service = LibraryService(library_datasource, hnsw_vector)
chunk_service = ChunkService(chunk_datasource, hnsw_vector)
document_service = DocumentService(document_datasource, hnsw_vector)
vector_service = VectorService(library_datasource, chunk_datasource, hnsw_vector)