from app.models import Library, Document
from app.storage import LibraryDataSource
from app.vector import VectorStore


class LibraryService:
    def __init__(self, library_datasource: LibraryDataSource, vector_store: VectorStore):
        self.libraries = library_datasource
        self.vector_store = vector_store

    def create(self, library: Library):
        """
        Create a new library and add the chunks of the documents to the vector store.
        """
        new_library = self.libraries.add(library)
        self.vector_store.add_vector_store(new_library.id)

        self.vector_store.add_library_chunks_if_needed(new_library)
            
        return new_library

    def read(self, library_id: int):
        return self.libraries.get(library_id)

    def delete(self, library_id: int):
        return self.libraries.remove(library_id)
