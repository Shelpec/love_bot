from aiogram import Router, F
from aiogram.types import Message
from datetime import datetime
from config import ADMIN_ID
from services.gemini import get_ai_response
import database.requests as rq

router = Router()

# Твоя дата (Год, Месяц, День)
START_DATE = datetime(2024, 1, 1) 

@router.message(F.text == "❤️ Наши воспоминания")
async def how_long_together(message: Message):
    # 1. Расчет времени
    now = datetime.now()
    delta = now - START_DATE
    days = delta.days
    
    # Текст сообщения
    base_text = (
        f"<b>Мы вместе уже:</b>\n"
        f"📆 {days} дней!\n"
        f"⏳ Это {days * 24} часов счастья.\n"
        f"Люблю тебя! ❤️"
    )
    
    # 2. Пытаемся найти фото
    memory = await rq.get_random_memory()
    
    if memory:
        # Если у фото было описание, добавим его
        caption_text = base_text
        if memory.caption:
            caption_text += f"\n\n💬 <i>Воспоминание: {memory.caption}</i>"
            
        # Отправляем медиа
        if memory.content_type == "photo":
            await message.answer_photo(memory.file_id, caption=caption_text, parse_mode="HTML")
        elif memory.content_type == "video":
            await message.answer_video(memory.file_id, caption=caption_text, parse_mode="HTML")
    else:
        # Если база пустая, отправляем просто текст
        await message.answer(base_text, parse_mode="HTML")

# Кнопка SOS
@router.message(F.text == "🆘 МНЕ ГРУСТНО")
async def sos_handler(message: Message):
    # Уведомление админу
    try:
        await message.bot.send_message(
            chat_id=ADMIN_ID, 
            text="🚨 <b>SOS!</b> Ей грустно! Напиши ей срочно!",
            parse_mode="HTML"
        )
    except: pass

    # Ответ бота
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    prompt = "Девушке грустно. Напиши короткое утешительное сообщение от имени любящего парня."
    support_text = await get_ai_response(message.from_user.id, prompt)
    await message.answer(support_text)