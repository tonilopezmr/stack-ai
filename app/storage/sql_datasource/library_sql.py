from app.models import Library, Document
from ..library_datasource import LibraryDataSource
from typing import Optional
from psycopg2.extras import Json
from .chunk_sql import ChunkPostgresDatasource
from psycopg2 import pool

class LibraryPostgresDatasource(LibraryDataSource):
    def __init__(self, chunk_sql_datasource: ChunkPostgresDatasource, connection_pool: pool.SimpleConnectionPool):
        self.connection_pool = connection_pool
        self.chunk_sql_datasource = chunk_sql_datasource        

    def add(self, library: Library) -> Library:
        connection = self.connection_pool.getconn()
        try:
            with connection.cursor() as cursor:
                cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                cursor.execute(
                    "INSERT INTO libraries (metadata) VALUES (%s) RETURNING id",
                    (Json(library.metadata),)
                )
                library.id = cursor.fetchone()[0]
                
                documents = []
                for document in library.documents:
                    cursor.execute(
                        "INSERT INTO documents (library_id, metadata) VALUES (%s, %s) RETURNING id",
                        (library.id, Json(document.metadata))
                    )                                        
                    document.id = cursor.fetchone()[0]                                      

                    chunks = []
                    for chunk in document.chunks:
                        new_chunk = self.chunk_sql_datasource.insert_chunk(cursor, document.id, chunk)
                        chunks.append(new_chunk)
                    
                    documents.append(Document(id=document.id, chunks=chunks, metadata=document.metadata))
                connection.commit()
        finally:
            self.connection_pool.putconn(connection)
        
        return Library(id=library.id, documents=documents, metadata=library.metadata)

    def get(self, library_id: int) -> Optional[Library]:
        connection = self.connection_pool.getconn()
        library = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                cursor.execute("""
                    SELECT l.id, l.metadata, d.id, d.metadata
                    FROM libraries l
                    LEFT JOIN documents d ON l.id = d.library_id
                    WHERE l.id = %s
                """, (library_id,))
                results = cursor.fetchall()
                
                if not results:
                    return None

                library_id, library_metadata = results[0][0], results[0][1]
                document_results = [(row[2], row[3]) for row in results if row[2] is not None]

                documents = []
                for document_id, document_metadata in document_results:
                    chunks = self.chunk_sql_datasource.get_chunks_by_document_id(document_id)
                    documents.append(Document(id=document_id, chunks=chunks, metadata=document_metadata))
                connection.commit()
                library = Library(id=library_id, documents=documents, metadata=library_metadata)            
        finally:
            self.connection_pool.putconn(connection)
        
        return library


    def remove(self, library_id: int) -> Optional[Library]:
        library = self.get(library_id)
        if library:
            connection = self.connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                    cursor.execute("DELETE FROM libraries WHERE id = %s", (library_id,))
                    connection.commit()  
            finally:
                self.connection_pool.putconn(connection)
        return library

    def update(self, library: Library) -> Library:
        connection = self.connection_pool.getconn()
        try:
            with connection.cursor() as cursor:
                cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                cursor.execute(
                    "UPDATE libraries SET metadata = %s WHERE id = %s",
                    (Json(library.metadata), library.id)
                )
                for document in library.documents:
                    if document.id is None:
                        cursor.execute(
                            "INSERT INTO documents (library_id, metadata) VALUES (%s, %s) RETURNING id",
                            (library.id, Json(document.metadata))
                        )
                        document.id = cursor.fetchone()[0]
                                        
                    for chunk in document.chunks:
                        if chunk.id is None:
                            new_chunk = self.chunk_sql_datasource.add(library.id, document.id, chunk)
                            chunk.id = new_chunk.id
                        else:
                            self.chunk_sql_datasource.update(library.id, chunk.id, chunk)
                connection.commit()  
        finally:
            self.connection_pool.putconn(connection)
        return library