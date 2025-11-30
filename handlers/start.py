from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.main_menu import main_kb
import database.requests as rq # <-- Импортируем наши запросы
from config import ADMIN_ID
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    # Сохраняем пользователя в БД
    await rq.set_user(message.from_user.id, message.from_user.first_name)
    
    await message.answer(
        "Привет, моя хорошая! ❤️\nЯ готов работать.",
        reply_markup=main_kb
    )

# Кнопка "Комплимент" теперь берет данные из БД!
@router.message(F.text == "💌 Комплимент")
async def send_compliment(message: Message):
    text = await rq.get_random_compliment()
    await message.answer(f"✨ {text}")



@router.message(Command("say"))
async def admin_say(message: Message):
    # Проверяем, что это ты
    if message.from_user.id != ADMIN_ID:
        return # Игнорируем чужих

    # Убираем команду /say из текста
    text_to_send = message.text[5:] 
    
    if not text_to_send:
        await message.answer("Напиши текст: /say Текст")
        return

    # Получаем ID девушки из базы (или просто отправь, если знаешь её ID)
    # Для простоты: бот ответит в тот же чат (тестируй сам). 
    # В реале тут нужен код: await message.bot.send_message(HER_ID, text_to_send)
    
    # Но пока сделаем эхо, чтобы ты проверил
    await message.answer(f"🗣 Я передал: {text_to_send}")
    
    # А вот так отправить ЕЙ (тебе нужно знать её ID):
    # await message.bot.send_message(chat_id=12345678, text=text_to_send)


@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "<b>📖 Что я умею (Инструкция):</b>\n\n"
        "🌤 <b>Погода</b> — точный прогноз и советы, что надеть.\n"
        "💌 <b>Комплимент</b> — если хочешь приятных слов.\n"
        "❤️ <b>Воспоминания</b> — наши фото и сколько мы вместе.\n"
        "🎁 <b>Подарок</b> — скинь мне фото/ссылку, и я сохраню это для Жанарыса.\n"
        "🔮 <b>Магия</b> — гадание на картах Таро.\n"
        "💡 <b>Куда сходим</b> — идеи для свиданий по погоде.\n"
        "🎲 <b>Игры</b> — Правда или Действие, Купоны.\n"
        "🆘 <b>Грустно</b> — нажми, если нужна поддержка.\n\n"
        "🎙 <b>Голосовые</b> — ты можешь отправлять мне голосовые, я понимаю!\n"
        "🎧 <b>Музыка</b> — напиши /music, чтобы получить трек."
    )
    await message.answer(text, parse_mode="HTML")