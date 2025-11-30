from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
import database.requests as rq

router = Router()

class WishState(StatesGroup):
    waiting_for_wish = State()

@router.message(F.text == "🎁 Хочу подарок")
async def start_wish(message: Message, state: FSMContext):
    await state.set_state(WishState.waiting_for_wish)
    await message.answer("Пришли мне фото, видео или текст желания 🎁")

@router.message(WishState.waiting_for_wish)
async def save_wish(message: Message, state: FSMContext):
    try:
        c_type = "text"
        file_id = None
        text = message.text

        # Обработка фото
        if message.photo:
            c_type = "photo"
            file_id = message.photo[-1].file_id
            text = message.caption # Может быть None, это нормально

        # Обработка видео
        elif message.video:
            c_type = "video"
            file_id = message.video.file_id
            text = message.caption

        # Сохранение
        await rq.add_wish(
            tg_id=message.from_user.id,
            text=text,
            file_id=file_id,
            c_type=c_type
        )
        
        await message.answer("✅ Записал в список желаний!")
        await state.clear()
        
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
        print(f"ERROR: {e}")
        await state.clear()

@router.message(F.text == "/my_princess_wishes")
async def show_wishes(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    wishes = await rq.get_all_wishes()
    if not wishes:
        await message.answer("Пусто 🤷‍♂️")
        return
        
    await message.answer("🎁 <b>Список желаний:</b>", parse_mode="HTML")
    
    for w in wishes:
        # Если текста нет, пишем просто дату
        caption_text = f"📝 {w.wish_text}" if w.wish_text else f"📅 {w.created_at.strftime('%d.%m')}"

        try:
            if w.content_type == "photo":
                await message.answer_photo(w.file_id, caption=caption_text)
            elif w.content_type == "video":
                await message.answer_video(w.file_id, caption=caption_text)
            else:
                await message.answer(f"🔸 {w.wish_text}")
        except Exception as e:
            await message.answer(f"Не грузится файл: {e}")