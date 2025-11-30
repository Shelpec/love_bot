from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database.requests as rq
from datetime import datetime, timedelta

router = Router()

class NoteState(StatesGroup):
    waiting_for_note = State()

class CycleState(StatesGroup):
    waiting_for_date = State()

# === ЗАМЕТКИ (СПИСОК ПОКУПОК) ===

@router.message(F.text == "📝 Общие заметки")
async def show_notes(message: Message):
    notes = await rq.get_notes()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить", callback_data="note_add"), 
         InlineKeyboardButton(text="🗑 Очистить всё", callback_data="note_clear")],
    ])
    
    if not notes:
        await message.answer("📝 <b>Список пуст!</b>\nМожно записать продукты или дела.", reply_markup=kb, parse_mode="HTML")
        return

    text = "<b>📝 Наш список:</b>\n\n"
    # Создаем кнопки для удаления каждой заметки
    rows = []
    for note in notes:
        text += f"▫️ {note.text}\n"
        rows.append([InlineKeyboardButton(text=f"❌ Удалить: {note.text[:10]}...", callback_data=f"del_note_{note.id}")])
    
    rows.append([InlineKeyboardButton(text="➕ Добавить", callback_data="note_add"), 
                 InlineKeyboardButton(text="🗑 Очистить всё", callback_data="note_clear")])
    
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@router.callback_query(F.data == "note_add")
async def start_add_note(callback: CallbackQuery, state: FSMContext):
    await state.set_state(NoteState.waiting_for_note)
    await callback.message.answer("Напиши, что добавить в список: 👇")
    await callback.answer()

@router.message(NoteState.waiting_for_note)
async def save_note(message: Message, state: FSMContext):
    await rq.add_note(message.text)
    await message.answer(f"✅ Добавлено: {message.text}")
    await state.clear()
    await show_notes(message) # Показываем обновленный список

@router.callback_query(F.data.startswith("del_note_"))
async def del_single_note(callback: CallbackQuery):
    note_id = int(callback.data.split("_")[2])
    await rq.delete_note(note_id)
    await callback.answer("Удалено!")
    await callback.message.delete() # Или обновить список

@router.callback_query(F.data == "note_clear")
async def clear_all_notes(callback: CallbackQuery):
    await rq.clear_notes()
    await callback.answer("Список очищен ✅")
    await callback.message.edit_text("📝 Список пуст!")

# === ТРЕКЕР ЦИКЛА (Care Tracker) ===

@router.message(F.text == "🌸 Мой цикл")
async def cycle_menu(message: Message):
    # Получаем данные
    cycle = await rq.get_cycle(message.from_user.id)
    
    if not cycle:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Отметить начало", callback_data="cycle_set_date")]
        ])
        await message.answer("🌸 <b>Трекер здоровья</b>\n\nЯ пока не знаю дату начала твоего цикла. Нажми кнопку, чтобы я мог заботиться о тебе.", reply_markup=kb, parse_mode="HTML")
        return

    # Расчеты
    last_date = cycle.last_period_date # date object
    cycle_len = cycle.cycle_length
    
    # Следующие месячные
    next_period = last_date + timedelta(days=cycle_len)
    # ПМС (за 5 дней до)
    pms_date = next_period - timedelta(days=5)
    # Овуляция (примерно середина, 14 дней до конца)
    ovulation = next_period - timedelta(days=14)
    
    days_left = (next_period - datetime.now().date()).days
    
    info = (
        f"🌸 <b>Твой календарь:</b>\n\n"
        f"🩸 Начало последних: <b>{last_date.strftime('%d.%m')}</b>\n"
        f"⏳ Цикл: <b>{cycle_len} дней</b>\n\n"
        f"🔜 Следующие ожидаем: <b>{next_period.strftime('%d.%m')}</b>\n"
        f"<i>(Через {days_left} дней)</i>\n\n"
        f"🍫 ПМС (напоминание парню): {pms_date.strftime('%d.%m')}\n"
        f"🥚 Овуляция: {ovulation.strftime('%d.%m')}"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🩸 Начались сегодня!", callback_data="cycle_today")],
        [InlineKeyboardButton(text="📅 Изменить дату", callback_data="cycle_set_date")]
    ])
    
    await message.answer(info, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data == "cycle_set_date")
async def ask_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CycleState.waiting_for_date)
    await callback.message.answer("Напиши дату начала последних месячных в формате: <b>ДД.ММ</b> (например: 23.11)", parse_mode="HTML")
    await callback.answer()

@router.message(CycleState.waiting_for_date)
async def set_cycle_date(message: Message, state: FSMContext):
    try:
        # Парсим дату (добавляем текущий год)
        date_str = message.text.strip()
        current_year = datetime.now().year
        full_date_str = f"{date_str}.{current_year}"
        
        start_date = datetime.strptime(full_date_str, "%d.%m.%Y").date()
        
        # Сохраняем
        await rq.set_cycle(message.from_user.id, start_date)
        
        await message.answer(f"✅ Записал! Начало цикла: {start_date.strftime('%d.%m.%Y')}")
        await state.clear()
        
    except ValueError:
        await message.answer("⚠️ Неверный формат. Попробуй еще раз: <b>ДД.ММ</b> (например 01.11)", parse_mode="HTML")

@router.callback_query(F.data == "cycle_today")
async def set_cycle_today(callback: CallbackQuery):
    today = datetime.now().date()
    await rq.set_cycle(callback.from_user.id, today)
    await callback.message.answer("✅ Обновил! Начало цикла — сегодня.")
    await callback.answer()