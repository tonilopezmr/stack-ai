from app.models import Document
from .. import DocumentDataSource
from .library_in_memory import LibraryInMemoryDatasource
from typing import Optional
import threading

class DocumentInMemoryDatasource(DocumentDataSource):
    def __init__(self, library_datasource: LibraryInMemoryDatasource):
        self.libraries = library_datasource
        self.lock = threading.Lock()

    def add(self, library_id: int, document: Document) -> Optional[Document]:
        with self.lock:
            library = self.libraries.get(library_id)
        
            if library:
                library.documents.append(document)
                return document

    def get(self, library_id: int, document_id: int) -> Optional[Document]:
        with self.lock:
            library = self.libraries.get(library_id)
            if library:
                for doc in library.documents:
                    if doc.id == document_id:
                        return doc

    def update(self, library_id: int, document: Document) -> Optional[Document]:
        with self.lock:
            library = self.libraries.get(library_id)
            if library:
                for i, existing_doc in enumerate(library.documents):
                    if existing_doc.id == document.id:
                        library.documents[i] = document
                        return document

    def remove(self, library_id: int, document_id: int) -> Optional[Document]:
        with self.lock:
            library = self.libraries.get(library_id)
            if library:
                for i, doc in enumerate(library.documents):
                    if doc.id == document_id:
                        del library.documents[i]
                        return doc
