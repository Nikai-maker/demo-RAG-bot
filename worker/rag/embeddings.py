from worker.config import Config
from worker.ai.ai_client import client
from typing import List
import asyncio
from abc import ABC, abstractmethod


class EmbeddingProcessor(ABC):
    """Абстрактный класс для создания эмбеддингов с поддержкой чанков"""

    @abstractmethod
    async def create_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """
        Принимает чанки и создаёт эмбеддинги.
        Возвращает список эмбеддингов.
        """
        pass

    @abstractmethod
    def max_chunk_length(self) -> int:
        """Возвращает максимальную длину чанка в токенах/символах"""
        pass

class OpenAIEmbeddingProcessor(EmbeddingProcessor):
    def __init__(self):
        pass

    def max_chunk_length(self) -> int:
        return 8191  # для text-embedding-3-small/large

    async def create_embeddings(self, chunks: List[str]) -> List[List[float]]:
        semaphore = asyncio.Semaphore(5)
        batch_size = 10

        async def _embed_batch(batch: List[str]) -> List[List[float]]:
            async with semaphore:
                try:
                    response = await client.embeddings.create(
                        model=Config.EMBEDDING_MODEL,
                        input=batch,
                        encoding_format="float",
                        dimensions=Config.EMBEDDING_DIM
                    )
                    return [data.embedding for data in response.data]
                except Exception as e:
                    print(f"Error embedding batch: {e}")
                    return [None] * len(batch)

        # Если чанков мало — отправляем одним запросом
        if len(chunks) <= batch_size:
            result = await _embed_batch(chunks)
            return [emb for emb in result if emb is not None]

        # Иначе делим на батчи
        batches = [chunks[i:i + batch_size] for i in range(0, len(chunks), batch_size)]
        all_embeddings = []
        for batch in batches:
            result = await _embed_batch(batch)
            all_embeddings.extend(result)
            await asyncio.sleep(0.1)  # rate limiting

        # Фильтруем ошибки
        return [emb for emb in all_embeddings if emb is not None]
