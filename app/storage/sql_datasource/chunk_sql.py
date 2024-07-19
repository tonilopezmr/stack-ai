from app.models import Chunk
from ..chunk_datasource import ChunkDataSource
from typing import Optional, List
from psycopg2 import pool
from psycopg2.extras import Json

class ChunkPostgresDatasource(ChunkDataSource):
    def __init__(self, connection_pool: pool.SimpleConnectionPool):
        self.connection_pool = connection_pool

    def add(self, library_id: int, document_id: int, chunk: Chunk) -> Optional[Chunk]:
        connection = self.connection_pool.getconn()
        new_chunk = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                new_chunk = self.insert_chunk(cursor, document_id, chunk)
                connection.commit()
        finally:
            self.connection_pool.putconn(connection)
        
        return new_chunk

    def insert_chunk(self, cursor, document_id: int, chunk: Chunk) -> Chunk:
        cursor.execute(
            "INSERT INTO chunks (document_id, text, embedding, metadata) VALUES (%s, %s, %s, %s) RETURNING id, document_id, text, embedding, metadata",
            (document_id, chunk.text, chunk.embedding, Json(chunk.metadata))
        )
        result = cursor.fetchone()        
        return Chunk(id=result[0], document_id=result[1], text=result[2], embedding=result[3], metadata=result[4])

    def get(self, library_id: int, chunk_id: int) -> Optional[Chunk]:
        connection = self.connection_pool.getconn()
        chunk = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                cursor.execute(
                    "SELECT id, document_id, text, embedding, metadata FROM chunks WHERE id = %s AND document_id IN (SELECT id FROM documents WHERE library_id = %s)",
                    (chunk_id, library_id)
                )
                result = cursor.fetchone()
                if result:
                    connection.commit()
                    chunk = Chunk(id=result[0], document_id=result[1], text=result[2], embedding=result[3], metadata=result[4])
        finally:
            self.connection_pool.putconn(connection)
        
        return chunk

    def update(self, library_id: int, chunk_id: int, chunk: Chunk) -> Optional[Chunk]:
        connection = self.connection_pool.getconn()
        updated_chunk = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                cursor.execute(
                    "UPDATE chunks SET text = %s, embedding = %s, metadata = %s WHERE id = %s AND document_id IN (SELECT id FROM documents WHERE library_id = %s) RETURNING id",
                    (chunk.text, chunk.embedding, Json(chunk.metadata), chunk_id, library_id)
                )
                if cursor.rowcount > 0:
                    connection.commit()
                    updated_chunk = Chunk(id=chunk_id, document_id=chunk.document_id, text=chunk.text, embedding=chunk.embedding, metadata=chunk.metadata)
        finally:
            self.connection_pool.putconn(connection)
        
        return updated_chunk

    def remove(self, library_id: int, chunk_id: int) -> Optional[Chunk]:
        chunk = self.get(library_id, chunk_id)
        if chunk:
            connection = self.connection_pool.getconn()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                    cursor.execute("DELETE FROM chunks WHERE id = %s", (chunk_id,))
                    connection.commit()
            finally:
                self.connection_pool.putconn(connection)
        return chunk

    def get_chunks_by_document_id(self, document_id: int) -> List[Chunk]:
        connection = self.connection_pool.getconn()
        chunks = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                cursor.execute(
                    "SELECT id, document_id, text, embedding, metadata FROM chunks WHERE document_id = %s",
                    (document_id,)
                )
                results = cursor.fetchall()
                if results:
                    connection.commit()
                    chunks = [Chunk(id=row[0], document_id=row[1], text=row[2], embedding=row[3], metadata=row[4]) for row in results]
        finally:
            self.connection_pool.putconn(connection)

        return chunks   