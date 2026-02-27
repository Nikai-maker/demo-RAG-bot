# ingestion.py
import uuid
from db import create_document, insert_chunks, mark_document_ready
from embeddings import generate_embeddings
from text_utils import extract_text, chunk_text


def process_document_job(payload: dict):
    tenant_id = uuid.UUID(payload["tenant_id"])
    filename = payload["filename"]
    file_path = payload["file_path"]

    document_id = create_document(tenant_id, filename)

    text = extract_text(file_path)
    chunks = chunk_text(text)

    enriched_chunks = []
    for chunk in chunks:
        embedding = generate_embeddings(chunk)
        enriched_chunks.append({
            "text": chunk,
            "embedding": embedding,
            "token_count": len(chunk.split())
        })

    insert_chunks(document_id, tenant_id, enriched_chunks)
    mark_document_ready(document_id)