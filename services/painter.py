import aiohttp
import random
import urllib.parse
from services.gemini import get_ai_response

BASE_URL = "https://image.pollinations.ai/prompt/"

async def generate_image(prompt_ru: str):
    """
    1. Переводит запрос.
    2. Генерирует ссылку.
    3. СКАЧИВАЕТ картинку в память бота.
    4. Возвращает байты (саму картинку) и промпт.
    """
    
    # 1. Перевод (чтобы нейросеть лучше понимала)
    translate_prompt = (
        f"Переведи этот запрос для генерации картинки на английский: '{prompt_ru}'. "
        "Сделай описание детальным, добавь 'high quality, 8k, masterpiece'. "
        "Верни ТОЛЬКО текст на английском."
    )
    # Если вдруг ИИ тупит, используем оригинал, но лучше перевести
    try:
        prompt_en = await get_ai_response(0, translate_prompt)
        prompt_en = prompt_en.replace('"', '').replace("'", "").strip()
    except:
        prompt_en = prompt_ru

    # 2. Формируем безопасную ссылку (кодируем пробелы)
    seed = random.randint(1, 100000)
    encoded_prompt = urllib.parse.quote(prompt_en) # Кодируем пробелы в %20
    
    # Добавляем параметры для красоты (Flux - крутая модель)
    url = f"{BASE_URL}{encoded_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"

    # 3. СКАЧИВАЕМ ФАЙЛ (Сами, а не просим Телеграм)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                image_bytes = await resp.read() # Читаем файл в память
                return image_bytes, prompt_en
            else:
                raise Exception(f"Ошибка сервера рисования: {resp.status}")