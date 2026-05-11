import os
from pathlib import Path


class Config:
    TELEGRAM_BOT_TOKEN=os.getenv('TELEGRAM_BOT_TOKEN')
    
    RABBITMQ_URL=os.getenv('RABBITMQ_URL')

    POSTGRES_HOST=os.getenv('POSTGRES_HOST')
    POSTGRES_PORT=os.getenv('POSTGRES_PORT')
    POSTGRES_DB=os.getenv('POSTGRES_DB')
    POSTGRES_USER=os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')

    OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')
    EMBEDDING_DIM=512
    EMBEDDING_MODEL="text-embedding-3-small"
    QUERY_EXPANSION_MODEL="gpt-3.5-turbo"
    RERANK_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RESPONSE_MODEL="gpt-3.5-turbo"
    RESPONSE_MAX_TOKENS=1000
    RESPONSE_MIN_TOKENS=100
    RESPONSE_TEMPERATURE=0.7
    INDEX_DIR = Path("indexes")
    PROMPT_FOR_EXPANSION = "Improve user's query with preparing it for the getting most relevant chunks from vector db"