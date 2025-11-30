from aiogram import Router, F
from aiogram.types import Message, PollAnswer, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.english import get_english_quiz
import database.requests as rq
import asyncio

router = Router()

class EnglishState(StatesGroup):
    learning = State()

stop_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🛑 Стоп (Показать статистику)")]], resize_keyboard=True)

# 1. ЗАПУСК
@router.message(F.text == "🇬🇧 Учить английский")
async def start_learning(message: Message, state: FSMContext):
    await state.set_state(EnglishState.learning)
    await message.answer("🚀 <b>Режим обучения!</b>\nСтатистика будет собираться.\nНажми 'Стоп', чтобы увидеть отчет.", reply_markup=stop_kb, parse_mode="HTML")
    await send_next_quiz(message, message.from_user.id, state)

# 2. ОБРАБОТКА ОТВЕТА
@router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer, bot, state: FSMContext):
    user_id = poll_answer.user.id
    
    # Получаем данные из памяти (какой ответ был правильным в прошлом вопросе)
    data = await state.get_data()
    correct_id = data.get("current_correct_id")
    
    # Если данные есть, проверяем
    if correct_id is not None:
        # poll_answer.option_ids - это список выбранных ответов (обычно один)
        chosen_id = poll_answer.option_ids[0]
        is_correct = (chosen_id == correct_id)
        
        # Записываем в базу
        await rq.log_quiz_attempt(user_id, is_correct)
    
    # Пауза для чтения объяснения
    await asyncio.sleep(3)
    
    # Следующий вопрос
    await send_next_quiz(bot, user_id, state)

# 3. ОТПРАВКА ВОПРОСА + СОХРАНЕНИЕ ПРАВИЛЬНОГО ОТВЕТА
async def send_next_quiz(messager, chat_id, state: FSMContext):
    sender = messager.bot if hasattr(messager, 'bot') else messager

    # Проверяем, не вышел ли юзер (если стейт сброшен, get_state вернет None)
    current_state = await state.get_state()
    if current_state != EnglishState.learning:
        return 

    quiz_data = await get_english_quiz(chat_id)
    
    if not quiz_data:
        await sender.send_message(chat_id, "Перерыв... (Ошибка AI)")
        return

    # ВАЖНО: Сохраняем ID правильного ответа в память, чтобы потом проверить
    await state.update_data(current_correct_id=quiz_data['correct_option_id'])

    await sender.send_poll(
        chat_id=chat_id,
        question=f"Word: {quiz_data['word']}",
        options=quiz_data['options'],
        type='quiz',
        correct_option_id=quiz_data['correct_option_id'],
        explanation=quiz_data['explanation'],
        is_anonymous=False 
    )

# 4. СТОП И ОТЧЕТ
@router.message(F.text == "🛑 Стоп (Показать статистику)")
async def stop_learning(message: Message, state: FSMContext):
    # Сначала получаем статистику
    stats = await rq.get_quiz_stats(message.from_user.id)
    
    # Очищаем состояние
    await state.clear()
    
    # Формируем отчет
    report = (
        "📊 <b>Твой отчет об успехах:</b>\n\n"
        f"📆 <b>За 24 часа:</b>\n"
        f"Ответов: {stats['day']['total']} | Верно: {stats['day']['correct']} ({stats['day']['percent']}%)\n\n"
        
        f"🗓 <b>За неделю:</b>\n"
        f"Ответов: {stats['week']['total']} | Верно: {stats['week']['correct']} ({stats['week']['percent']}%)\n\n"
        
        f"📅 <b>За месяц:</b>\n"
        f"Ответов: {stats['month']['total']} | Верно: {stats['month']['correct']} ({stats['month']['percent']}%)\n\n"
        "Ты молодец! Keep going! 🇬🇧"
    )
    
    from keyboards.main_menu import main_kb 
    await message.answer(report, reply_markup=main_kb, parse_mode="HTML")