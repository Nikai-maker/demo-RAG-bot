# embeddings.py
import os
from typing import List

# Если используешь OpenAI
try:
    import openai
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("Не задан OpenAI API ключ в переменной OPENAI_API_KEY")
    openai.api_key = OPENAI_API_KEY
except ImportError:
    openai = None


def generate_embeddings(text: str) -> List[float]:
    """
    Генерация эмбеддингов для текста.
    Использует OpenAI API (text-embedding-3-large) или возвращает заглушку.
    """
    if openai:
        resp = openai.Embedding.create(
            input=text,
            model="text-embedding-3-large"
        )
        return resp["data"][0]["embedding"]
    else:
        # Заглушка: для теста возвращает 1536 нулей
        return [0.0] * 1536


if __name__ == "__main__":
    # тестовый запуск
    sample_text = "Привет! Это тест."
    emb = generate_embeddings(sample_text)
    print(f"Длина эмбеддинга: {len(emb)}")
    print(emb[:10], "...")  # первые 10 значений