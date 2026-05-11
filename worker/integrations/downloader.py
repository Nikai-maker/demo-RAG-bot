from anyio import Path
from abc import ABC, abstractmethod

class FileDownloader(ABC):
    """Абстрактный класс для скачивания файлов из разных платформ"""
    @abstractmethod
    async def download_file(self, link: str) -> Path:
        """Скачать файл по его id и вернуть путь к нему"""
        pass