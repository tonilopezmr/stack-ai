from abc import ABC, abstractmethod
from typing import Optional
from app.models import Chunk

class ChunkDataSource(ABC):

    @abstractmethod
    def add(self, library_id: int, document_id: int, chunk: Chunk) -> Optional[Chunk]:
        pass

    @abstractmethod
    def get(self, chunk_id: int) -> Optional[Chunk]:
        pass

    @abstractmethod
    def remove(self, chunk_id: int) -> Optional[Chunk]:
        pass

    @abstractmethod
    def update(self, chunk_id: int, chunk: Chunk) -> Optional[Chunk]:
        pass
