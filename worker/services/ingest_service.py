from worker.config import Config
from worker.integrations.tg_downloader import TelegramDownloader
from worker.rag.files_handler import PDFHandler
from typing import List, Dict
from worker.repositories.embeddings_repository import EmbeddingsRepository
from worker.repositories.chunks_repository import ChunksRepository
from worker.repositories.docs_repository import DocsRepository


class IngestService():
    """Сервис для обработки и загрузки документов в базу данных"""
    def __init__(
            self,
            splitter,
            embedding_processor,
            docs_repository: DocsRepository,
            chunks_repository: ChunksRepository,
            embeddings_repository: EmbeddingsRepository
        ):
        self.splitter = splitter
        self.embedding_processor = embedding_processor
        self.docs_repository = docs_repository
        self.chunks_repository = chunks_repository
        self.embeddings_repository = embeddings_repository


    def _get_downloader(self, service):
        """Получить загрузчик по имени сервиса"""
        if service == "telegram":
            return TelegramDownloader(Config.TELEGRAM_BOT_TOKEN)
        else:
            raise ValueError(f"Unsupported service: {service}")
        
    def _get_file_handler(self, file_type):
        """Получить обработчик по типу файла"""
        if file_type == "pdf":
            return PDFHandler()
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    async def _download_file(self, downloader, file_id) -> str:
        """Скачать файл в temp и вернуть путь к нему"""
        return await downloader.download_file(await downloader.get_file_path(file_id))

    def _extract_text(self, file_handler, file_path) -> str:
        """Извлечь текст из файла"""
        return file_handler.extract_text(file_path)
    
    async def _save_document(self, user_id, file_name, text) -> int:
        """Сохранить документ в БД"""
        return await self.docs_repository.save_document(user_id, file_name, text)
    
    def _split_text(self, text) -> List[Dict[str, str]]:
        """Разбить текст на части"""
        return self.splitter.split_text(text)
    
    async def _save_chunks(self, document_id, chunks) -> list[int]:
        """Сохранить чанки в БД"""
        return await self.chunks_repository.save_chunks(document_id, chunks)
    
    async def _create_embeddings(self, chunks) -> List[List[float]]:
        """Создать эмбеддинги для текстов чанков"""
        texts = [chunk["text"] for chunk in chunks]
        return await self.embedding_processor.create_embeddings(texts)
    
    async def _save_embeddings(self, chunk_ids, embeddings) -> list[int]:
        """Сохранить эмбеддинги в БД"""
        return await self.embeddings_repository.save_embeddings(chunk_ids, embeddings)
    
    async def _reindex_bm25(self, user_id: int):
        """Пересчитать BM25 индекс"""
        await self.chunks_repository.reindex_bm25(user_id)

    async def ingest_process(self, user_id, message) -> dict:
        """Обработать документ и сохранить его в БД. Оркестрация"""
        downloader = self._get_downloader(message["service"])
        file_handler = self._get_file_handler(message["file_type"])
        file_path = await self._download_file(downloader, message["file_id"])
        file_text = self._extract_text(file_handler, file_path)
        doc_id = await self._save_document(user_id, message["file_name"], file_text)
        chunks = self._split_text(file_text)
        saved_chunk_ids = await self._save_chunks(doc_id, chunks)
        embeddings = await self._create_embeddings(chunks)
        await self._save_embeddings(saved_chunk_ids, embeddings)
        await self._reindex_bm25(user_id)

        return {
            "status": "success",
            "user_id": user_id,
            "doc_id": doc_id,
            "platform": message["service"],
            "chunks_count": len(chunks),
        }
