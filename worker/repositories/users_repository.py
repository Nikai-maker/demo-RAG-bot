from worker.db.db import Database


class UsersRepository():
    def __init__(self, db: Database):
        self.db = db

    async def get_or_create_user(self, platform_id: int, name: str) -> int:
        """Создание или получение нового пользователя"""
        query = """
        INSERT INTO users (platform_id, name, created_at)
        VALUES ($1, $2, NOW())
        ON CONFLICT (platform_id) DO NOTHING
        RETURNING id;
        """
        result = await self.db.fetchrow(query, platform_id, name)

        if result:
            return result["id"]
        else:
            # уже существует — получаем id
            row = await self.db.fetchrow("SELECT id FROM users WHERE platform_id = $1", platform_id)
            if row is None:
                raise RuntimeError("User not found after conflict check")
            return row["id"]
