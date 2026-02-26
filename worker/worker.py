import psycopg2
from pgvector.psycopg2 import register_vector

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
conn.autocommit = True
register_vector(conn)

# Создать таблицу с векторным полем
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        filename TEXT,
        chunk_text TEXT,
        embedding vector(1536),  -- для OpenAI embeddings
        metadata JSONB
    )
""")

# Поиск похожих документов
cur.execute("""
    SELECT chunk_text, 1 - (embedding <=> %s) as similarity
    FROM documents
    ORDER BY embedding <=> %s
    LIMIT 5
""", (embedding, embedding))