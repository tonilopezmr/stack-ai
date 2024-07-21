from app.models import Document
from app.storage import DocumentDataSource
from app.vector import VectorStore


class DocumentService:
    def __init__(self, document_datasource: DocumentDataSource, vector_store: VectorStore):
        self.documents = document_datasource
        self.vector_store = vector_store

    def create(self, library_id: int, document: Document):
        """
        Create a new document and add the chunks of the document to the vector store.
        """
        new_document = self.documents.add(library_id, document)
        self.vector_store.add_document_chunks_if_needed(library_id, new_document)
        return new_document

    def read(self, library_id: int, document_id: int):
        return self.documents.get(library_id, document_id)

    def update(self, library_id: int, document: Document):
        updated_document = self.documents.update(library_id, document)
        self.vector_store.add_document_chunks_if_needed(library_id, updated_document)
        return updated_document

    def delete(self, library_id: int, document_id: int):
        document = self.documents.get(library_id, document_id)
        if not document:
            return None
        
        self.documents.remove(library_id, document_id)

        print("DOCUMENT", document)
        for chunk in document.chunks:
            self.vector_store.delete_vector(library_id, chunk.id)
        return document
