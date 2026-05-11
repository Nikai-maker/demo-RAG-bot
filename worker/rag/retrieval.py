from worker.config import Config
from worker.rag.embeddings import EmbeddingProcessor
from worker.rag.generation import Generator
from sentence_transformers import CrossEncoder
from worker.repositories.chunks_repository import ChunksRepository


class Retrieval():
    def __init__(
            self,
            re_ranker: CrossEncoder,
            responser: Generator,
            embedding_processor: EmbeddingProcessor,
            chunks_repository: ChunksRepository
        ):
        self.re_ranker = re_ranker
        self.responser = responser
        self.embedding_processor = embedding_processor
        self.chunks_repository = chunks_repository

    async def _query_expansion(self, system_prompt: str, user_prompt: str) -> str:
        """Функция для улучшения запроса пользователя"""
        return await self.responser.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
    
    async def _create_embedding(self, query: str) -> list[float]:
        """Функция для создания эмбеддинга для запроса"""
        embedding = await self.embedding_processor.create_embeddings([query])
        return embedding[0]

    async def _get_relevant_chunks_by_embeddings(self, embedding: list[float], user_id: int) -> list[str]:
        """Функция для получения релевантных чанков по эмбеддингам"""
        return await self.chunks_repository.get_relevant_chunks(embedding, user_id)

    async def _get_relevant_chunks_by_bm25(self, query: str, user_id: int) -> list[str]:
        """Функция для получения релевантных чанков по bm25"""
        return await self.chunks_repository.get_relevant_chunks_by_bm25(query, user_id)
    
    def _combine_chunks(self, chunks_by_vector: list[dict], chunks_by_bm25: list[dict]) -> list[dict]:
        """Объединяем чанки по вектору и bm25"""""
        combined_chunks = []
        seen_ids = set()
        for chunk in chunks_by_vector + chunks_by_bm25:
            if chunk["id"] not in seen_ids:
                combined_chunks.append(chunk)
                seen_ids.add(chunk["id"])
        return combined_chunks

    async def _reranking(self, query: str, chunks: list[dict]) -> list[str]:
        """Реранкинг чанков"""
        try:
            query_doc_pairs = [(query, chunk["text"]) for chunk in chunks]
            scores = self.re_ranker.predict(query_doc_pairs)
            ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
            ranked_texts = [chunk["text"] for chunk, score in ranked[:5]]
            return ranked_texts
        except Exception as e:
            print(f"Ошибка при reranking'е: {e}")
            # Fallback: возвращаем первые 5 текстов
            return [chunk["text"] for chunk in chunks[:5]]
        
    async def retrieve(self, query: str, user_id: int) -> list[str]:
        """Основная функция для получения ответа"""
        system_prompt_for_expansion = Config.PROMPT_FOR_EXPANSION
        expand_query = await self._query_expansion(system_prompt_for_expansion, query)
        embedding = await self._create_embedding(expand_query)
        relevant_chunks_by_embeddings = await self._get_relevant_chunks_by_embeddings(embedding, user_id)
        relevant_chunks_by_bm25 = await self._get_relevant_chunks_by_bm25(expand_query, user_id)
        combine_chunks = self._combine_chunks(relevant_chunks_by_embeddings, relevant_chunks_by_bm25)
        reranked_chunks = await self._reranking(expand_query, combine_chunks)
        return reranked_chunks
