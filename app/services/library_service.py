import threading
from app.models import Library

class LibraryService:
    def __init__(self):
        self.libraries = {}
        self.lock = threading.Lock()

    def create_library(self, library: Library):
        with self.lock:
            self.libraries[library.id] = library
        
        return library

    def read_library(self, library_id: int):
        with self.lock:
            return self.libraries.get(library_id)

    def update_library(self, library_id: int, library: Library):
        with self.lock:
            self.libraries[library_id] = library
            return library

    def delete_library(self, library_id: int):
        with self.lock:
            library = self.libraries[library_id]
            del self.libraries[library_id]
            return library
