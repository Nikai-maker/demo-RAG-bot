from worker.db.db import Database


class DocsRepository():
    def __init__(self, db: Database):
        self.db = db

    async def save_document(self, user_id: int, file_name: str, file_text: str) -> int:
        """Сохраняет документ в БД и возвращает его id"""
        return await self.db.fetchval(
                "INSERT INTO docs (user_id, doc_name, doc_text, created_at) VALUES ($1, $2, $3, NOW()) RETURNING id",
                user_id, file_name, file_text
            )
    
