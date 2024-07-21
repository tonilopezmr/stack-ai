from abc import ABC, abstractmethod
from typing import Optional
from app.models import Document

class DocumentDataSource(ABC):

    @abstractmethod
    def add(self, library_id: int, document: Document) -> Optional[Document]:
        pass

    @abstractmethod
    def get(self, library_id: int, document_id: int) -> Optional[Document]:
        pass

    @abstractmethod
    def update(self, library_id: int, document: Document) -> Optional[Document]:
        pass

    @abstractmethod
    def remove(self, library_id: int, document_id: int) -> Optional[Document]:
        pass
