import google.generativeai as genai
from config import GEMINI_KEY
import logging
from datetime import datetime, timedelta
import collections
import os 
import json


# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Настройка модели
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
else:
    logging.error("GEMINI_KEY не найден!")
    model = None

# === ПАМЯТЬ БОТА ===
chat_histories = {}

def get_system_prompt():
    now = datetime.now().strftime("%d %B %Y года, время %H:%M")
    return f"""
    ТВОЯ РОЛЬ:
    Ты — высокоинтеллектуальный персональный ассистент (похож на Джарвиса или Альфреда).
    Ты вежлив, лаконичен, умен и полезен.
    Твоего создателя зовут Жанарыс.
    
    ТЕКУЩИЙ КОНТЕКСТ:
    Сегодня: {now} (Твой часовой пояс — Казахстан/Астана).
    Ты общаешься с девушкой Жанарыса.
    
    ПРАВИЛА:
    1. Не здоровайся постоянно.
    2. Будь краток и мил.
    """

# --- ТЕКСТОВЫЙ ОТВЕТ ---
async def get_ai_response(user_id: int, user_text: str):
    if not model:
        return "Системы ИИ отключены (нет ключа)."

    try:
        if user_id not in chat_histories:
            chat_histories[user_id] = collections.deque(maxlen=15)
        
        history = chat_histories[user_id]
        
        # Формируем историю текстом
        history_text = ""
        for role, text in history:
            history_text += f"{role}: {text}\n"

        full_prompt = (
            f"{get_system_prompt()}\n\n"
            f"ИСТОРИЯ ДИАЛОГА:\n{history_text}\n"
            f"НОВОЕ СООБЩЕНИЕ: {user_text}\n"
            f"ОТВЕТ:"
        )

        response = await model.generate_content_async(full_prompt)
        answer = response.text

        history.append(("User", user_text))
        history.append(("Model", answer))

        return answer
    except Exception as e:
        logging.error(f"Ошибка Gemini: {e}")
        return "Малыш, я немного задумался... Повтори ❤️"

# --- ГОЛОСОВОЙ ОТВЕТ (Этой функции у тебя не хватало) ---
async def get_ai_response_voice(user_id: int, voice_path: str):
    if not model:
        return "Мои уши (API) не подключены..."

    try:
        # 1. Загружаем файл в Google
        uploaded_file = genai.upload_file(voice_path)
        
        # 2. Формируем промпт
        system_text = get_system_prompt()
        prompt = "Послушай это голосовое сообщение от девушки и ответь ей так, как будто ты её парень-помощник. Будь краток и мил."
        
        # 3. Отправляем
        response = await model.generate_content_async([system_text, uploaded_file, prompt])
        
        # 4. Удаляем файл из Google (чистим за собой)
        try:
            uploaded_file.delete()
        except: pass

        # 5. Сохраняем в историю
        if user_id not in chat_histories:
            chat_histories[user_id] = collections.deque(maxlen=15)
        
        chat_histories[user_id].append(("User", "[Голосовое сообщение]"))
        chat_histories[user_id].append(("Model", response.text))

        return response.text

    except Exception as e:
        logging.error(f"Ошибка Gemini Voice: {e}")
        return "Я не расслышал... Можешь написать текстом? ❤️"
    



async def get_image_description(image_path: str, user_style: str):
    if not model: return None

    try:
        # 1. Загружаем файл в Google
        uploaded_file = genai.upload_file(image_path)
        
        # 2. Промпт для Gemini
        # Мы просим его описать фото визуально и добавить стиль
        prompt = (
            f"Look at this image. Describe the main subject, their pose, clothes, colors, and background in great detail. "
            f"Combine this description with the style: '{user_style}'. "
            f"Create a prompt for an image generator (Stable Diffusion). "
            f"Write ONLY the prompt in English."
        )
        
        # 3. Генерируем описание
        response = await model.generate_content_async([uploaded_file, prompt])
        
        # 4. Удаляем файл
        try: uploaded_file.delete()
        except: pass
        
        return response.text

    except Exception as e:
        logging.error(f"Ошибка Gemini Vision: {e}")
        return None
    


# --- ПАРСЕР ВРЕМЕНИ (ЧЕРЕЗ ИИ) ---
async def parse_reminder(user_text: str):
    """
    Принимает текст: "Напомни через 10 минут выключить духовку"
    Возвращает: datetime object и текст задачи.
    """
    if not model: return None, None

    # Текущее время для контекста
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Системный промпт для парсинга
    prompt = f"""
    Current time: {now}.
    User request: "{user_text}".
    
    Task: Extract the exact date/time for the reminder and the reminder text itself.
    
    Rules:
    1. Calculate the target time based on "Current time".
    2. If user says "in 10 minutes", add 10 mins to current time.
    3. If user says "tomorrow at 9", find tomorrow's date and set time 09:00.
    4. Return ONLY raw JSON format: {{"target_time": "YYYY-MM-DD HH:MM:SS", "task": "text"}}
    5. If you cannot find time, return {{"error": "no_time"}}
    """
    
    try:
        response = await model.generate_content_async(prompt)
        text_resp = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text_resp)
        
        if "error" in data:
            return None, None
            
        target_dt = datetime.strptime(data["target_time"], "%Y-%m-%d %H:%M:%S")
        return target_dt, data["task"]
        
    except Exception as e:
        logging.error(f"Ошибка парсинга напоминания: {e}")
        return None, None