# search.py
from db import get_conn


def search_similar_chunks(tenant_id, query_embedding, limit=5):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT chunk_text,
                   1 - (embedding <=> %s) AS similarity
            FROM document_chunks
            WHERE tenant_id = %s
            ORDER BY embedding <=> %s
            LIMIT %s
        """, (query_embedding, tenant_id, query_embedding, limit))

        results = cur.fetchall()

    return [
        {"text": row[0], "similarity": float(row[1])}
        for row in results
    ]