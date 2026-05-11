import aiohttp
import tempfile
import os
from worker.integrations.downloader import FileDownloader
from anyio import Path

class TelegramDownloader(FileDownloader):
    """Клиент для скачивания файлов из Telegram по id"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

    async def get_file_path(self, file_id: str) -> str:
        """Получить путь к файлу в Telegram по его id"""
        link = f"{self.base_url}/getFile?file_id={file_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                if resp.status != 200:
                    raise Exception(f"Ошибка получения пути к файлу: {resp.status}")
                data = await resp.json()
                return data["result"]["file_path"]

    async def download_file(self, link: str) -> Path:
        """Скачать файл из телеграм во временную папку и вернуть путь к нему"""
        
        url = f"https://api.telegram.org/file/bot{self.token}/{link}"

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_path = temp_file.name  # Путь к файлу
        temp_file.close()  # Закрываем файл, чтобы потом перезаписать

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise Exception(f"Ошибка скачивания файла: {resp.status}")
                    with open(temp_path, 'wb') as f:
                        f.write(await resp.read())
                return temp_path
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)  # Удаляем временный файл при ошибке
            raise e
