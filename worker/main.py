from worker.config import Config
from worker.db.db import Database
from worker.queue.producer import push_message
from worker.rag.generation import OpenAIGenerator
from worker.rag.retrieval import Retrieval
from worker.rag.embeddings import OpenAIEmbeddingProcessor
from worker.rag.text_splitter import OpenAITextSplitter
from worker.repositories.users_repository import UsersRepository
from worker.repositories.docs_repository import DocsRepository
from worker.repositories.chunks_repository import ChunksRepository
from worker.repositories.embeddings_repository import EmbeddingsRepository
from worker.services.ingest_service import IngestService
from worker.services.query_service import QueryService
from sentence_transformers import CrossEncoder


db = Database()
re_ranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
generator = OpenAIGenerator()
embedding_processor = OpenAIEmbeddingProcessor()
splitter = OpenAITextSplitter()
users_repository = UsersRepository(db)
docs_repository = DocsRepository(db)
chunks_repository = ChunksRepository(db)
embeddings_repository = EmbeddingsRepository(db)
retrieval = Retrieval(
    re_ranker=re_ranker,
    responser=generator,
    embedding_processor=embedding_processor,
    chunks_repository=chunks_repository
)
ingest_service = IngestService(
    splitter=splitter,
    embedding_processor=embedding_processor,
    docs_repository=docs_repository,
    chunks_repository=chunks_repository,
    embeddings_repository=embeddings_repository
)
query_service = QueryService(retrieval=retrieval, generator=generator)


async def handle_message(message: object):
    user_id = await users_repository.get_or_create_user(message["chat_id"], message["name"])
    if message["task_type"] == "upload":
        message_body = await ingest_service.ingest_process(user_id, message)
    elif message["task_type"] == "query":
        message_body = await query_service.query_process(user_id, message)
    else:
        raise ValueError(f"Unsupported task_type: {message['task_type']}")

    push_message(message_body)
