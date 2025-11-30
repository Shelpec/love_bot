from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from services.gemini import get_ai_response, get_ai_response_voice
from services.voice_out import text_to_speech_file
import os

router = Router()

# Кнопка под ответом ИИ
def get_voice_kb(text_hash):
    # Мы не можем засунуть весь текст в кнопку (лимит), поэтому просто ставим маркер
    # В идеале нужно хранить текст в кэше, но для простоты просто сделаем кнопку "Озвучить последнее"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗣 Озвучить", callback_data="tts_read")]
    ])

@router.message(F.text)
async def chat_with_ai(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    ai_answer = await get_ai_response(message.from_user.id, message.text)
    
    # Отправляем ответ с кнопкой "Озвучить"
    # Сохраняем текст ответа в "памяти" этого сообщения (через reply_to не выйдет просто так)
    # Хак: просто отправляем текст. А когда нажмет кнопку - возьмем текст сообщения.
    await message.answer(ai_answer, reply_markup=get_voice_kb("idx"))

@router.callback_query(F.data == "tts_read")
async def read_aloud(callback: CallbackQuery):
    text = callback.message.text
    if not text:
        await callback.answer("Текста нет!")
        return

    await callback.answer("Записываю голосовое...")
    await callback.bot.send_chat_action(chat_id=callback.message.chat.id, action="record_voice")
    
    # Генерируем голос
    try:
        # Берем первые 200 символов для названия файла
        filename = f"tts_{callback.message.message_id}"
        file_path = text_to_speech_file(text, filename)
        
        voice = FSInputFile(file_path)
        await callback.message.reply_voice(voice)
        
        # Удаляем файл
        os.remove(file_path)
    except Exception as e:
        await callback.answer(f"Ошибка озвучки: {e}")

# ... (хэндлер для голосовых F.voice оставь как был) ...
@router.message(F.voice)
async def chat_with_voice(message: Message):
    # (Вставь сюда код из предыдущего урока, если он пропал)
    # Кратко продублирую:
    await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_voice")
    file = await message.bot.get_file(message.voice.file_id)
    file_path = f"downloads/{message.voice.file_id}.ogg"
    if not os.path.exists("downloads"): os.makedirs("downloads")
    await message.bot.download_file(file.file_path, file_path)
    try:
        ai_answer = await get_ai_response_voice(message.from_user.id, file_path)
        await message.answer(ai_answer, reply_markup=get_voice_kb("idx"))
    finally:
        if os.path.exists(file_path): os.remove(file_path)