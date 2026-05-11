from worker.rag.generation import Generator
from worker.rag.retrieval import Retrieval


class QueryService():
    """Сервис для обработки запросов"""
    def __init__(
            self,
            retrieval: Retrieval,
            generator: Generator
        ):
        self.retrieval = retrieval
        self.generator = generator

    async def _get_relevant_chunks(self, query, user_id):
        """Возвращает релевантные чанки по запросу пользователя"""
        return await self.retrieval.retrieve(query, user_id)

    async def _generate_response(self, query: str, context: str) -> str:
        system_prompt = f"You are a helpful assistant. Answer based on the context:\n\n{context}"
        return await self.generator.generate(
            system_prompt=system_prompt,
            user_prompt=query
        )

    async def query_process(self, user_id: int, message: dict) -> dict:
        query = message["message"]
        relevant_chunks = await self._get_relevant_chunks(query, user_id)
        context = "\n\n".join(relevant_chunks)
        response = await self._generate_response(query, context)
        return {
            "status": "success",
            "user_id": user_id,
            "platform": message["service"],
            "response": response
        }
