from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
from database.core import async_session
from database.models import User
from sqlalchemy import select
from datetime import datetime
import database.requests as rq

router = Router()

# --- Загрузка фото (Память) ---
class UploadMemory(StatesGroup):
    waiting_for_media = State()

@router.message(Command("add_memory"))
async def start_upload(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.set_state(UploadMemory.waiting_for_media)
    await message.answer("📸 Присылай фото для воспоминаний. /cancel для выхода.")

@router.message(UploadMemory.waiting_for_media)
async def uploading(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("✅ Выход.")
        return

    try:
        file_id, c_type, caption = None, "photo", message.caption
        if message.photo:
            file_id = message.photo[-1].file_id
        elif message.video:
            file_id = message.video.file_id
            c_type = "video"
        else:
            await message.answer("Жду фото/видео.")
            return

        await rq.add_memory(file_id, c_type, caption)
        await message.answer("💾 Сохранил!")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

# --- Чревовещатель ---
@router.message(Command("say"))
async def cmd_say(message: Message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.answer("Пример: /say Текст")
        return
    text_to_send = args[1]
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for user in users:
            if user.tg_id != ADMIN_ID:
                try: await message.bot.send_message(chat_id=user.tg_id, text=text_to_send)
                except: pass
        await message.answer("✅ Отправлено.")

# --- ДАТЫ (События) ---
@router.message(Command("add_date"))
async def add_important_date(message: Message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            await message.answer("Формат: `/add_date 01.01.2000 Название`", parse_mode="Markdown")
            return
        
        date_obj = datetime.strptime(parts[1], "%d.%m.%Y").date()
        await rq.add_event(parts[2], date_obj)
        await message.answer(f"✅ Запомнил: {parts[2]} — {parts[1]}")
        
    except ValueError:
        await message.answer("Ошибка в дате! Формат ДД.ММ.ГГГГ")

@router.message(Command("dates"))
async def show_dates(message: Message):
    if message.from_user.id != ADMIN_ID: return
    
    # ВОТ ЗДЕСЬ БЫЛА ОШИБКА, ТЕПЕРЬ ФУНКЦИЯ ЕСТЬ
    events = await rq.get_all_events()
    
    if not events:
        await message.answer("Список дат пуст.")
        return
        
    text = "📅 <b>Важные даты:</b>\n"
    for e in events:
        text += f"▪️ {e.event_date.strftime('%d.%m')} — {e.name} (ID: {e.id})\n"
    
    text += "\nУдалить: `/del_date ID`"
    await message.answer(text, parse_mode="HTML")

@router.message(Command("del_date"))
async def del_date(message: Message):
    if message.from_user.id != ADMIN_ID: return
    try:
        event_id = int(message.text.split()[1])
        await rq.delete_event(event_id)
        await message.answer("🗑 Удалено.")
    except:
        await message.answer("Ошибка ID.")