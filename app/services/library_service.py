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

        for document in new_library.documents:
            self.add_document_vectors_if_needed(new_library.id, document)
            
        return new_library

    def read(self, library_id: int):
        return self.libraries.get(library_id)

    def delete(self, library_id: int):
        return self.libraries.remove(library_id)

    def has_chunks(self, document: Document) -> bool:
        return len(document.chunks) > 0

    def add_document_vectors_if_needed(self, library_id: int, document: Document):
        """
        Add vectors of a document's chunks to the vector store.

        Args:
            library_id (int): The identifier of the library.
            document (Document): The document containing chunks with vectors.
        """
        if self.has_chunks(document):
            for chunk in document.chunks:
                self.vector_store.add_vector(library_id, chunk.id, chunk.embedding, chunk.metadata)
