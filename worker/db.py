# db.py
import os
import uuid
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector

DB_CONFIG = dict(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT", 5432),
)

@contextmanager
def get_conn():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    register_vector(conn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_schema():
    """Создание таблиц и индексов"""
    with get_conn() as conn:
        cur = conn.cursor()

        # Расширение pgvector
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Tenants
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id UUID PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # Documents (метаданные файла)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            filename TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # Chunks
        cur.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id UUID PRIMARY KEY,
            document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            tenant_id UUID NOT NULL,
            chunk_text TEXT NOT NULL,
            embedding vector(1536) NOT NULL,
            token_count INT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

        # Индекс для vector search
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_chunks_embedding
        ON document_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """)

        # Индекс для multi-tenant фильтрации
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_chunks_tenant
        ON document_chunks (tenant_id);
        """)

        cur.execute("ANALYZE document_chunks;")


def create_document(tenant_id: str, filename: str, status: str = "processing") -> str:
    """Создать запись о документе и вернуть его UUID"""
    doc_id = str(uuid.uuid4())
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO documents (id, tenant_id, filename, status)
            VALUES (%s, %s, %s, %s)
        """, (doc_id, tenant_id, filename, status))
    return doc_id


def insert_chunks(document_id: str, tenant_id: str, chunks: list):
    """Вставка чанков документа в документные куски"""
    values = []
    for chunk in chunks:
        values.append((
            str(uuid.uuid4()),
            document_id,
            tenant_id,
            chunk["text"],
            chunk["embedding"],  # должен быть list[float] длиной 1536
            chunk.get("token_count", None)
        ))
    with get_conn() as conn:
        cur = conn.cursor()
        execute_values(
            cur,
            """
            INSERT INTO document_chunks (id, document_id, tenant_id, chunk_text, embedding, token_count)
            VALUES %s
            """,
            values
        )


def mark_document_ready(document_id: str):
    """Пометить документ как обработанный"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE documents SET status = 'ready' WHERE id = %s
        """, (document_id,))