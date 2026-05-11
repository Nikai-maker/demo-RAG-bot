import os

from worker.db.db import Database
from worker.config import Config
from worker.rag.bm25_indexer import BM25Indexer


class ChunksRepository():
    def __init__(self, db: Database):
        self.db = db

    async def save_chunks(self, doc_id: int, chunks: list[dict]) -> list[int]:
        """Сохранить чанки в БД"""
        chunk_ids = []
        for chunk in chunks:
            chunk_id = await self.db.fetchval(
                "INSERT INTO chunks (doc_id, text, created_at) VALUES ($1, $2, NOW()) RETURNING id",
                doc_id, chunk["text"]  # предполагаем, что chunk — это dict с ключом "text"
            )
            chunk_ids.append(chunk_id)
        return chunk_ids
    
    async def get_relevant_chunks(self, query: list[float], user_id: int) -> list[dict]:
        """Получить релевантные чанки из БД по запросу в embedding формате и user_id"""
        return await self.db.fetch(
            """
            SELECT c.id, c.text
            FROM chunks c
            JOIN embeddings e ON c.id = e.chunk_id
            JOIN docs d ON c.doc_id = d.id
            WHERE d.user_id = $1
            ORDER BY e.vector <=> $2
            LIMIT 5;
            """,
            user_id, query
        )
    
    async def get_relevant_chunks_by_bm25(self, query: str, user_id: int) -> list[dict]:
        """Получить релевантные чанки из БД по bm25"""
        index_path = Config.INDEX_DIR / f"user_{user_id}.pkl"
        if not index_path.exists():
            raise FileNotFoundError(f"Файл индекса не найден: {index_path}")
        indexer = BM25Indexer.load(index_path)
        return indexer.search(query, k=10)

    async def reindex_bm25(self, user_id: int) -> None:
        """Пересобрать BM25 индекс пользователя из всех его чанков"""
        Config.INDEX_DIR.mkdir(exist_ok=True)
        all_chunks = await self.db.fetch(
            """
            SELECT c.id, c.text
            FROM chunks c
            JOIN docs d ON c.doc_id = d.id
            WHERE d.user_id = $1
            """,
            user_id
        )

        index_path = Config.INDEX_DIR / f"user_{user_id}.pkl"
        if all_chunks:
            chunk_list = [{"id": chunk["id"], "text": chunk["text"]} for chunk in all_chunks]
            indexer = BM25Indexer(chunk_list)
            indexer.save(index_path)
            return

        if index_path.exists():
            os.remove(index_path)
