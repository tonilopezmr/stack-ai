from app.services import ChunkService, LibraryService
from app.storage import ChunkInMemoryDatasource, LibraryInMemoryDatasource

library_datasource = LibraryInMemoryDatasource()
chunk_datasource = ChunkInMemoryDatasource(library_datasource)

library_service = LibraryService(library_datasource)
chunk_service = ChunkService(chunk_datasource)