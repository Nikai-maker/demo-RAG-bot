import pickle
import nltk
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
from typing import List, Dict

nltk.download('punkt', quiet=True)

class BM25Indexer:
    """Класс для создания и использования BM25-индекса для текстовых данных"""

    def __init__(self, chunk_list: List[Dict]):
        """
        :param chunk_list: [{"id": int, "text": str}, ...]
        """
        self.chunks = chunk_list
        self.tokenized_corpus = [word_tokenize(chunk["text"].lower()) for chunk in chunk_list]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def save(self, filepath: str):
        """Сохраняет индекс и данные на диск"""
        data = {
            "chunks": self.chunks,
            "tokenized_corpus": self.tokenized_corpus
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

    def search(self, query: str, k=5) -> List[Dict]:
        """
        Ищет топ-k релевантных чанков.
        :return: Список словарей с ключами 'id', 'text'
        """
        tokenized_query = word_tokenize(query.lower())
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [self.chunks[i] for i in top_indices]

    @classmethod
    def load(cls, filepath: str):
        """Загружает индекс с диска и воссоздаёт BM25-индекс"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        # Пересоздаём объект класса
        instance = cls.__new__(cls)
        instance.chunks = data["chunks"]
        instance.tokenized_corpus = data["tokenized_corpus"]
        instance.bm25 = BM25Okapi(instance.tokenized_corpus)
        return instance