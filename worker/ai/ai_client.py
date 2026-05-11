from worker.config import Config
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
