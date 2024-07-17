from app.services import ChunkService, LibraryService

library_service = LibraryService()
chunk_service = ChunkService(library_service)