from worker.config import Config
import asyncpg

class Database:
    def __init__(self):
        self.pool = None  # Пул соединений

    async def connect(self):
        """Создает пул соединений к PostgreSQL"""
        if self.pool is not None:
            return
        self.pool = await asyncpg.create_pool(
            host=Config.POSTGRES_HOST,
            port=Config.POSTGRES_PORT,
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD,
            database=Config.POSTGRES_DB,
            min_size=1,  # Минимальное количество соединений
            max_size=10  # Максимальное количество соединений
        )
        print("Connected to PostgreSQL")

    async def close(self):
        """Закрывает пул соединений"""
        if self.pool:
            await self.pool.close()

    async def fetch(self, query: str, *args):
        """Выполняет SELECT и возвращает результат"""
        if self.pool is None:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
        
    async def fetchrow(self, query: str, *args):
        """Выполняет SELECT и возвращает одну строку или None"""
        if self.pool is None:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, query: str, *args):
        """Выполняет INSERT, UPDATE, DELETE"""
        if self.pool is None:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
        
    async def executemany(self, query: str, args_list):
        """
        Выполняет запрос несколько раз для списка аргументов (массовая вставка/обновление)
        """
        if self.pool is None:
            await self.connect()
        async with self.pool.acquire() as conn:
            await conn.executemany(query, args_list)

    async def fetchval(self, query: str, *args):
        if self.pool is None:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)
