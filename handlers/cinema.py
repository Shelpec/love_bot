from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database.requests as rq
from services.gemini import get_ai_response
import random

router = Router()

class CinemaState(StatesGroup):
    waiting_for_title = State()

# --- МЕНЮ КИНО ---
@router.message(F.text == "🎬 Кино-Комната")
async def open_cinema(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Список 'Хотим посмотреть'", callback_data="movie_list")],
        [InlineKeyboardButton(text="➕ Добавить фильм", callback_data="movie_add")],
        [InlineKeyboardButton(text="🎲 Случайный из списка", callback_data="movie_random")],
        [InlineKeyboardButton(text="🤖 Посоветуй (AI)", callback_data="movie_ai_suggest")]
    ])
    await message.answer("Добро пожаловать в ваш личный кинотеатр! 🍿\nЧто будем делать?", reply_markup=kb)

# --- ДОБАВЛЕНИЕ ФИЛЬМА ---
@router.callback_query(F.data == "movie_add")
async def start_add_movie(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CinemaState.waiting_for_title)
    await callback.message.edit_text("Напиши название фильма или сериала, который хочешь посмотреть: 👇")

@router.message(CinemaState.waiting_for_title)
async def save_movie(message: Message, state: FSMContext):
    await rq.add_movie(message.text, message.from_user.id)
    await message.answer(f"✅ Фильм «{message.text}» добавлен в список!")
    await state.clear()
    # Возвращаем меню
    await open_cinema(message)

# --- СПИСОК ФИЛЬМОВ ---
@router.callback_query(F.data == "movie_list")
async def show_list(callback: CallbackQuery):
    movies = await rq.get_movies()
    if not movies:
        await callback.answer("Список пуст! Добавь что-нибудь.", show_alert=True)
        return

    text = "<b>🍿 Ваш список просмотра:</b>\n\n"
    kb_builder = []
    
    for m in movies:
        text += f"▪️ {m.title}\n"
        # Кнопка удаления для каждого фильма (чтобы отметить как просмотренное)
        kb_builder.append([InlineKeyboardButton(text=f"✅ Посмотрели: {m.title[:15]}...", callback_data=f"del_movie_{m.id}")])
    
    kb_builder.append([InlineKeyboardButton(text="🔙 Назад", callback_data="movie_back")])
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_builder), parse_mode="HTML")

# --- УДАЛЕНИЕ ---
@router.callback_query(F.data.startswith("del_movie_"))
async def delete_movie(callback: CallbackQuery):
    movie_id = int(callback.data.split("_")[2])
    await rq.delete_movie(movie_id)
    await callback.answer("Отметила как просмотренное! 🗑")
    # Обновляем список
    await show_list(callback)

# --- СЛУЧАЙНЫЙ ---
@router.callback_query(F.data == "movie_random")
async def random_movie(callback: CallbackQuery):
    movies = await rq.get_movies()
    if not movies:
        await callback.answer("Список пуст!", show_alert=True)
        return
    
    movie = random.choice(movies)
    await callback.message.answer(f"🎲 Жребий брошен! \n\nСегодня смотрим: <b>«{movie.title}»</b>! 🍿", parse_mode="HTML")

# --- ИИ СОВЕТЧИК ---
@router.callback_query(F.data == "movie_ai_suggest")
async def ai_suggest_menu(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😂 Комедия", callback_data="rec_comedy"), InlineKeyboardButton(text="😱 Ужасы", callback_data="rec_horror")],
        [InlineKeyboardButton(text="😭 Драма", callback_data="rec_drama"), InlineKeyboardButton(text="🤯 Триллер", callback_data="rec_thriller")],
        [InlineKeyboardButton(text="🦄 Мультик", callback_data="rec_cartoon"), InlineKeyboardButton(text="🔙 Назад", callback_data="movie_back")]
    ])
    await callback.message.edit_text("Какой жанр вы хотите?", reply_markup=kb)

@router.callback_query(F.data.startswith("rec_"))
async def get_recommendation(callback: CallbackQuery):
    genre_map = {
        "rec_comedy": "легкую комедию", "rec_horror": "страшный хоррор",
        "rec_drama": "трогательную мелодраму или драму", "rec_thriller": "захватывающий триллер с крутым сюжетом",
        "rec_cartoon": "добрый мультфильм (Disney/Pixar/Anime)"
    }
    genre = genre_map.get(callback.data, "фильм")
    
    await callback.message.edit_text("🤔 Подбираю лучший фильм для вас...")
    
    prompt = f"Посоветуй один крутой {genre} для просмотра парой. Напиши название, год, рейтинг и почему стоит посмотреть (очень кратко, 2 предложения)."
    response = await get_ai_response(callback.from_user.id, prompt)
    
    await callback.message.edit_text(f"🍿 <b>Рекомендация:</b>\n\n{response}", parse_mode="HTML")

# --- НАЗАД ---
@router.callback_query(F.data == "movie_back")
async def back_to_cinema(callback: CallbackQuery):
    await callback.message.delete()
    await open_cinema(callback.message)