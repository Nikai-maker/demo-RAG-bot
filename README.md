# Сервис (пет-проект) - RAG бот

## Архитектура:
Каналы (сейчас - Telegram). Файлы (сейчас - pdf)
+
n8n
+
RabbitMQ
+
Python Worker с LLM для embeddings и generation (сейчас - OpenAI)
+
PostgreSQL