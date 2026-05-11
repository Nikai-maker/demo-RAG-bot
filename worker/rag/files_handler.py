from abc import ABC, abstractmethod


class FileHandler(ABC):
    """Абстрактный класс для обработки файлов разных форматов"""
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        pass

class PDFHandler(FileHandler):
    """Обработчик для PDF файлов"""
    def extract_text(self, file_path) -> str:
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 library is required to handle PDF files. Please install it using 'pip install PyPDF2'.")
        
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'
            return text