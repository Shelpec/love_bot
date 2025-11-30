from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database.requests as rq

router = Router()

class SavingsState(StatesGroup):
    waiting_for_goal = State()
    waiting_for_amount = State()

# --- ПРОГРЕСС БАР ---
def get_progress_bar(current, target, length=10):
    if target == 0: return "[░░░░░░░░░░] 0%"
    percent = current / target
    if percent > 1: percent = 1
    filled_length = int(length * percent)
    bar = "█" * filled_length + "░" * (length - filled_length)
    return f"[{bar}] {int(percent * 100)}%"

# --- МЕНЮ КОПИЛКИ ---
@router.message(F.text == "💰 Семейная Копилка")
async def show_savings(message: Message):
    saving = await rq.get_savings()
    
    if not saving:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎯 Создать цель", callback_data="save_new")]])
        await message.answer("💰 У нас пока нет финансовой цели.\nДавай создадим?", reply_markup=kb)
        return

    bar = get_progress_bar(saving.current_amount, saving.target_amount)
    
    # Форматирование чисел (1 000 000)
    cur_fmt = "{:,}".format(saving.current_amount).replace(",", " ")
    tar_fmt = "{:,}".format(saving.target_amount).replace(",", " ")
    left_fmt = "{:,}".format(saving.target_amount - saving.current_amount).replace(",", " ")

    text = (
        f"💰 <b>Цель: {saving.goal_name}</b>\n\n"
        f"{bar}\n"
        f"💵 Собрано: <b>{cur_fmt} ₸</b>\n"
        f"🏁 Надо: <b>{tar_fmt} ₸</b>\n"
        f"Осталось: {left_fmt} ₸"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Внести деньги", callback_data="save_deposit")],
        [InlineKeyboardButton(text="🔄 Изменить цель", callback_data="save_new")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

# --- СОЗДАНИЕ ЦЕЛИ ---
@router.callback_query(F.data == "save_new")
async def start_new_goal(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SavingsState.waiting_for_goal)
    await callback.message.edit_text("На что будем копить? (Напиши название, например: 'Отпуск в Дубае')")

@router.message(SavingsState.waiting_for_goal)
async def get_goal_name(message: Message, state: FSMContext):
    if not message.text: return
    await state.update_data(name=message.text)
    await state.set_state(SavingsState.waiting_for_amount)
    await message.answer("Сколько нужно денег? (Напиши число, например: 1000000)")

@router.message(SavingsState.waiting_for_amount)
async def get_goal_amount(message: Message, state: FSMContext):
    if not message.text: return
    try:
        # Убираем пробелы если есть (1 000 000 -> 1000000)
        amount_str = message.text.replace(" ", "").replace(".", "")
        amount = int(amount_str)
        
        data = await state.get_data()
        await rq.set_savings_goal(data['name'], amount)
        
        await message.answer(f"🎯 Цель установлена: <b>{data['name']}</b> на {amount} тенге!", parse_mode="HTML")
        await state.clear()
        await show_savings(message)
    except ValueError:
        await message.answer("Пожалуйста, введи просто число (без букв).")

# --- ВНЕСЕНИЕ ДЕНЕГ ---
@router.callback_query(F.data == "save_deposit")
async def ask_deposit(callback: CallbackQuery):
    await callback.message.answer("Сколько закидываем в копилку? (Напиши просто сумму, например: 5000)")
    await callback.answer()

# --- ЛОВИМ СУММУ (ФИКС ОШИБКИ) ---
# Теперь мы проверяем x.text, что он не None
@router.message(lambda x: x.text and x.text.isdigit() and int(x.text) > 0)
async def process_deposit(message: Message):
    amount = int(message.text)
    saving = await rq.add_money(amount)
    
    if saving:
        fmt_amount = "{:,}".format(amount).replace(",", " ")
        await message.answer(f"✅ Добавлено <b>{fmt_amount} ₸</b>!\nМы стали ближе к мечте!", parse_mode="HTML")
        await show_savings(message)