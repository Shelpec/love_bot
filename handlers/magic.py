from aiogram import Router, F
from aiogram.types import Message
from services.gemini import get_ai_response
import random

router = Router()

TAROT_CARDS = [
    "Шут", "Маг", "Жрица", "Императрица", "Император", "Влюбленные", 
    "Колесница", "Сила", "Отшельник", "Колесо Фортуны", "Справедливость", 
    "Солнце", "Луна", "Звезда", "Мир", "Суд"
]

@router.message(F.text == "🔮 Магия и Таро")
async def magic_tarot(message: Message):
    # 1. Выбираем случайную карту
    card = random.choice(TAROT_CARDS)
    
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # 2. Просим Gemini описать её значение для любви
    prompt = (
        f"Девушка вытянула карту Таро: '{card}'. "
        "Дай короткое, мистическое и позитивное толкование этой карты в контексте любви и отношений на сегодня. "
        "Будь загадочным, как астролог."
    )
    
    prediction = await get_ai_response(0, prompt)
    
    await message.answer(f"🎴 <b>Твоя карта дня: {card}</b>\n\n{prediction}", parse_mode="HTML")