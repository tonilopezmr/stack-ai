from psycopg2 import pool
import os

# Create a connection pool
connection_pool = pool.SimpleConnectionPool(
    1,  # Minimum number of connections
    10, # Maximum number of connections
    dbname=os.getenv('POSTGRES_DB', 'stack_ai_database'),
    user=os.getenv('POSTGRES_USER', 'user1'),
    password=os.getenv('POSTGRES_PASSWORD', 'dbpassword'),
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=int(os.getenv('POSTGRES_PORT', 5432))
)

def initialize_postgresql():
    connection = connection_pool.getconn()    

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS libraries (
                    id SERIAL PRIMARY KEY,
                    metadata JSONB NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    library_id INTEGER NOT NULL,
                    metadata JSONB NOT NULL,
                    FOREIGN KEY (library_id) REFERENCES libraries (id) ON DELETE CASCADE
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    embedding FLOAT8[] NOT NULL,
                    metadata JSONB NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
                );
            """)
    finally:
        connection_pool.putconn(connection)

    return connection_pool