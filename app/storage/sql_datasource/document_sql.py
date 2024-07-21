from app.models import Document, Chunk
from .. import DocumentDataSource, ChunkPostgresDatasource
from typing import Optional
from psycopg2.extras import Json
from psycopg2 import pool

class DocumentPostgresDatasource(DocumentDataSource):
    def __init__(self, chunk_sql_datasource: ChunkPostgresDatasource, connection_pool: pool.SimpleConnectionPool):
        self.connection_pool = connection_pool
        self.chunk_sql_datasource = chunk_sql_datasource        

    def add(self, library_id: int, document: Document) -> Optional[Document]:
        with self.connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                cursor.execute(
                    """
                    INSERT INTO documents (library_id, metadata)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (library_id, Json(document.metadata))
                )
                document_id = cursor.fetchone()[0]
                
                for chunk in document.chunks:
                    self.chunk_sql_datasource.insert_chunk(cursor, document_id, chunk)
                
                conn.commit()
                document.id = document_id
                return document

    def get(self, library_id: int, document_id: int) -> Optional[Document]:
        with self.connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                cursor.execute(
                    """
                    SELECT d.id, d.metadata, c.id, c.text, c.embedding, c.metadata
                    FROM documents d
                    LEFT JOIN chunks c ON d.id = c.document_id
                    WHERE d.id = %s AND d.library_id = %s
                    """,
                    (document_id, library_id)
                )
                rows = cursor.fetchall()

                conn.commit()
                if rows:
                    document_id, document_metadata = rows[0][0], rows[0][1]
                    chunks = [
                        Chunk(id=row[2], text=row[3], embedding=row[4], metadata=row[5])
                        for row in rows if row[2] is not None
                    ]
                    return Document(id=document_id, chunks=chunks, metadata=document_metadata)
                return None
        
        
    def update(self, library_id: int, document: Document) -> Optional[Document]:
        with self.connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                cursor.execute(
                    """
                    UPDATE documents
                    SET metadata = %s
                    WHERE id = %s AND library_id = %s
                    RETURNING id
                    """,
                    (Json(document.metadata), document.id, library_id)
                )
                document_id = cursor.fetchone()[0]
                conn.commit()
                return self.get(library_id, document_id)

    def remove(self, library_id: int, document_id: int) -> Optional[Document]:
        with self.connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                cursor.execute(
                    """
                    DELETE FROM documents
                    WHERE id = %s AND library_id = %s
                    RETURNING id, metadata
                    """,
                    (document_id, library_id)
                )
                row = cursor.fetchone()
                conn.commit()
                if row:
                    return Document(id=row[0], metadata=row[1], chunks=[])
                return None
