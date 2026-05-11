import tiktoken
from typing import List, Dict
from abc import ABC, abstractmethod


class TextSplitter(ABC):
    """Абстрактный класс для разбиения текста на чанки"""
    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        pass

class OpenAITextSplitter(TextSplitter):
    def __init__(self, chunk_size: int = 500, overlap: int = 75):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, file_text: str) -> List[Dict[str, str]]:
        tokens = self.encoding.encode(file_text)
        chunks = []
        step = self.chunk_size - self.overlap
        for i in range(0, len(tokens), step):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append({
                "id": len(chunks),  # временный id — индекс
                "text": chunk_text.strip()
            })
        return chunks