from worker.db.db import Database
from worker.config import Config


class EmbeddingsRepository():
    def __init__(self, db: Database):
        self.db = db

    async def save_embeddings(self, chunk_ids: list[int], embeddings: list[list[float]]) -> bool:
        """Сохраняем эмбеддинги в БД"""
        insert_data = []
        for chunk_id, vector in zip(chunk_ids, embeddings):
            insert_data.append((chunk_id, vector, Config.EMBEDDING_MODEL))
        await self.db.executemany(
            """
            INSERT INTO embeddings (chunk_id, vector, model_name, created_at, updated_at)
            VALUES ($1, $2, $3, NOW(), NOW())
            """,
            insert_data
        )
        return True
