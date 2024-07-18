from app.services import ChunkService, LibraryService, VectorService
from app.storage import ChunkInMemoryDatasource, LibraryInMemoryDatasource
from app.vector import BruteForceVectorStore

library_datasource = LibraryInMemoryDatasource()
chunk_datasource = ChunkInMemoryDatasource(library_datasource)
vector_store = BruteForceVectorStore()

library_service = LibraryService(library_datasource, vector_store)
chunk_service = ChunkService(chunk_datasource, vector_store)
vector_service = VectorService(chunk_datasource, vector_store)