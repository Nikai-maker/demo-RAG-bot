from abc import ABC, abstractmethod
from ..ai.ai_client import client
from worker.config import Config


class Generator(ABC):
    """Абстрактный класс для генерации ответа"""

    @abstractmethod
    async def generate(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        min_tokens: int = 1,
        temperature: float = 0.7
    ) -> str:
        """
        Генерация текста.

        :param model: Модель для генерации
        :param system_prompt: Системный промт
        :param user_prompt: Пользовательский запрос + контекст
        :param max_tokens: Максимальное число токенов
        :param min_tokens: Минимальное число токенов
        :return: Сгенерированный текст
        """
        pass

class OpenAIGenerator(Generator):
    def __init__(self, api_client=None):
        self.client = api_client or client  # возможность подмены клиента (для тестов)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = Config.RESPONSE_MODEL,
        max_tokens: int = Config.RESPONSE_MAX_TOKENS,
        min_tokens: int = Config.RESPONSE_MIN_TOKENS,
        temperature: float = Config.RESPONSE_TEMPERATURE
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                min_tokens=min_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Логируйте ошибку, если у вас есть логгер
            raise RuntimeError(f"Ошибка при генерации ответа через OpenAI: {e}")
