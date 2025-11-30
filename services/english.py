import json
import random
from services.gemini import model
import database.requests as rq
import logging

async def get_english_quiz(user_id: int):
    if not model: return None

    # 1. Получаем список слов, которые НЕЛЬЗЯ использовать
    banned_words = await rq.get_banned_words(user_id)
    banned_str = ", ".join(banned_words)

    # 2. ЖЕСТКИЙ ПРОМПТ
    prompt = f"""
    Role: You are an English teacher for Russian students.
    Task: Generate 1 vocabulary quiz question (Level: Pre-Intermediate).
    
    Constraints:
    1. Pick a useful English word NOT in this list: [{banned_str}].
    2. The 'correct' and 'wrong' options MUST be strictly in RUSSIAN language (Translations).
    3. Do NOT provide definitions in English. Only Russian translations.
    
    JSON Format required:
    {{
        "word": "Ambiguous",
        "correct": "Двусмысленный",
        "wrong": ["Прозрачный", "Амбициозный", "Твердый"],
        "example": "His answer was ambiguous. - Его ответ был двусмысленным."
    }}
    """

    try:
        response = await model.generate_content_async(prompt)
        # Чистим ответ от markdown (```json ... ```)
        text_resp = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text_resp)
        
        # Записываем слово в историю
        await rq.update_word_stat(user_id, data["word"])
        
        options = data["wrong"]
        correct_answer = data["correct"]
        
        # Проверка на дурака: если ИИ вдруг выдал английский, пробуем перевести (редкий кейс, но пусть будет)
        # Но с новым промптом это маловероятно.
        
        options.append(correct_answer)
        random.shuffle(options)
        
        correct_id = options.index(correct_answer)
        
        # Формируем объяснение
        explanation = f"✅ Перевод: {correct_answer}\n\n📝 Пример:\n{data['example']}"

        return {
            "word": data["word"],
            "options": options,
            "correct_option_id": correct_id,
            "explanation": explanation[:200] # Лимит телеграма
        }

    except Exception as e:
        logging.error(f"Ошибка квиза: {e}")
        return None