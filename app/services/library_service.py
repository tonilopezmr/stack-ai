from app.models import Library
from app.storage import LibraryDataSource
from fastapi import HTTPException

class LibraryService:
    def __init__(self, library_datasource: LibraryDataSource):
        self.libraries = library_datasource

    def create(self, library: Library):
        return self.libraries.add(library)

    def read(self, library_id: int):
        return self.libraries.get(library_id)

    def update(self, library_id: int, library: Library):
        return self.libraries.update(library_id, library)

    def delete(self, library_id: int):
        return self.libraries.remove(library_id)
