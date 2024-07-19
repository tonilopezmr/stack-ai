from app.models import Library
from ..library_datasource import LibraryDataSource
from typing import Optional

import threading

class LibraryInMemoryDatasource(LibraryDataSource):
    def __init__(self):
        self.library_storage = {}
        self.lock = threading.Lock()

    def add(self, library: Library) -> Library:
        with self.lock:
            self.library_storage[library.id] = library
        return library

    def get(self, library_id: int) -> Optional[Library]:
        with self.lock:
            return self.library_storage.get(library_id)

    def remove(self, library_id: int) -> Optional[Library]:
        with self.lock:
            if library_id in self.library_storage:            
                library = self.library_storage[library_id]
                del self.library_storage[library_id]
                return library

    def update(self, library: Library) -> Library:
        with self.lock:
            self.library_storage[library.id] = library
        return library
