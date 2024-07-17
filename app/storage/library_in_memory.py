from app.models import Library
from .library_datasource import LibraryDataSource
from typing import Optional

class LibraryInMemoryDatasource(LibraryDataSource):
    def __init__(self):
        self.library_storage = {}

    def add(self, library: Library) -> Library:
        self.library_storage[library.id] = library
        return library

    def get(self, library_id: int) -> Optional[Library]:
        return self.library_storage.get(library_id)

    def remove(self, library_id: int) -> Optional[Library]:
        if library_id in self.library_storage:            
            library = self.library_storage[library_id]
            del self.library_storage[library_id]
            return library

    def update(self, library_id: int, library: Library) -> Library:
        self.library_storage[library_id] = library
        return library
