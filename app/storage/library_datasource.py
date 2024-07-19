from abc import ABC, abstractmethod
from typing import Optional
from app.models import Library

class LibraryDataSource(ABC):

    @abstractmethod
    def add(self, library: Library) -> Library:
        pass

    @abstractmethod
    def get(self, library_id: int) -> Optional[Library]:
        pass

    @abstractmethod
    def remove(self, library_id: int) -> Optional[Library]:
        pass

    @abstractmethod
    def update(self, library: Library) -> Library:
        pass
    