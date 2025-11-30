from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.fun_kb import get_games_kb
from services.gemini import get_ai_response
from services.downloader import search_batch, download_track_fast
from config import ADMIN_ID
import random
import os

router = Router()

COUPONS = [
    # --- РОМАНТИКА И НЕЖНОСТИ ---
    "Массаж спины (20 минут)",
    "Массаж ног с кремом",
    "Массаж головы и перебирание волос",
    "100 поцелуев прямо сейчас",
    "Обнимашки (минимум 10 минут без перерыва)",
    "Завтрак в постель",
    "Романтическая ванна с пеной (я всё подготовлю)",
    "Вечер при свечах без телефонов",
    "Я ношу тебя на руках (буквально)",
    "Комплимент каждый час в течение дня",
    "Медленный танец под нашу музыку",

    # --- ЕДА И ВКУСНЯШКИ ---
    "Ужин в ресторане (я плачу)",
    "Заказ любой еды на дом (суши/пицца/бургеры)",
    "Я готовлю твое любимое блюдо",
    "Поход за мороженым/кофе прямо сейчас",
    "Я чищу тебе фрукты (мандарины/гранат)",
    "Кофе в постель утром",
    "День вредной еды (без диет и угрызений совести)",
    "Ты выбираешь ресторан для свидания",
    "Покупка любой шоколадки по твоему требованию",

    # --- ПОМОЩЬ И БЫТ (Самое ценное!) ---
    "Освобождение от мытья посуды (я мою)",
    "Я выношу мусор вне очереди",
    "Генеральная уборка одной комнаты (я делаю)",
    "Я глажу твою одежду",
    "Поход в магазин со списком (ты отдыхаешь)",
    "Я заправляю кровать неделю",
    "Полный выходной от домашних дел",
    "Я мою полы во всей квартире",
    "Встретить тебя с работы/учебы",

    # --- РАЗВЛЕЧЕНИЯ ---
    "Киновечер (фильм выбираешь ТЫ)",
    "Поход в кино на места для поцелуев",
    "Твоя музыка в машине всю поездку",
    "Совместная прогулка в парке",
    "Играем в настолку/приставку (даже если я не хочу)",
    "Фотосессия (я фоткаю тебя, пока не понравится)",
    "Поездка по ночному городу",
    "Идем туда, куда ты давно хотела",
    "День шоппинга (я ношу пакеты и не ною)",

    # --- СПАСАТЕЛЬНЫЕ КРУГИ (ДЖОКЕРЫ) ---
    "День без обид (прощаю любой косяк)",
    "Право на 'Я же говорила!'",
    "Победа в споре (автоматически)",
    "Отмена любого моего решения",
    "Честный ответ на любой вопрос",
    "Я признаю, что был не прав",
    "Вето на встречу (не идем туда, куда ты не хочешь)",
    "Любое желание (в пределах разумного)",
    "Повтор любого предыдущего купона",
    "Абонемент на 'Хочу на ручки'"
]

MUSIC_QUERIES = {
    "sad": ["Ninety One", "Joji", "Sadraddin", "Billie Eilish", "Adele", "Tom Odell", "Lana Del Rey"],
    "love": ["Moldanazar", "Ed Sheeran", "M'Dee", "John Legend", "Taylor Swift", "Bruno Mars"],
    "party": ["Ninety One", "Alpha Q-pop", "The Weeknd", "Dua Lipa", "Black Eyed Peas", "Macklemore"]
}

TRUTH_THEMES = [
    "о наших отношениях и будущем",
    "о самых смешных и неловких моментах в жизни",
    "о тайных желаниях и фантазиях (романтично)",
    "о детстве и школьных годах",
    "провокационный вопрос, чтобы узнать друг друга глубже",
    "вопрос 'что бы ты выбрала'",
    "о том, что ей нравится во мне (парне)"
]

DARE_THEMES = [
    "милое и романтичное действие с парнем",
    "смешное задание, чтобы мы посмеялись",
    "задание, связанное с телефоном или соцсетями",
    "легкое физическое задание (массаж, обнимашки)",
    "изобразить кого-то или что-то",
    "дерзкое и игривое задание"
]

class PlayerState(StatesGroup):
    playing = State()

@router.message(F.text == "🎲 Игры для нас")
async def open_games(message: Message):
    await message.answer("Развлечения 👇", reply_markup=get_games_kb())

# --- МУЗЫКА ---
@router.callback_query(F.data == "game_music")
async def music_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😢 Грустно (Soul)", callback_data="start_sad")],
        [InlineKeyboardButton(text="❤️ Романтика (Love)", callback_data="start_love")],
        [InlineKeyboardButton(text="💃 Движ (Party)", callback_data="start_party")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_back")]
    ])
    
    if callback.message.audio:
        await callback.message.delete()
        await callback.message.answer("Выбери настроение: 🎧", reply_markup=kb)
    else:
        await callback.message.edit_text("Выбери настроение: 🎧", reply_markup=kb)

@router.callback_query(F.data.startswith("start_"))
async def start_playlist(callback: CallbackQuery, state: FSMContext):
    mood = callback.data.split("_")[1]
    query_base = random.choice(MUSIC_QUERIES.get(mood, ["Ninety One"]))
    
    await callback.message.edit_text(f"🚀 Загружаю плейлист: <b>{query_base}</b>...\nЖдем пару секунд...")
    
    tracks = await search_batch(query_base, limit=15)
    random.shuffle(tracks)
    
    if not tracks:
        await callback.message.edit_text("Не нашел треков :( Попробуй другой жанр.")
        return

    await state.set_state(PlayerState.playing)
    await state.update_data(queue=tracks, mood=mood)
    await play_next_song(callback.message, state, first_time=True)

@router.callback_query(F.data == "next_track", PlayerState.playing)
async def next_track_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await play_next_song(callback.message, state, first_time=False)

async def play_next_song(message: Message, state: FSMContext, first_time: bool):
    data = await state.get_data()
    queue = data.get('queue', [])
    mood = data.get('mood', 'music')
    
    if not queue:
        await message.answer("Плейлист закончился! Выбери новый.", reply_markup=get_games_kb())
        await state.clear()
        return

    track = queue.pop(0)
    await state.update_data(queue=queue)
    
    if first_time:
        msg = await message.answer(f"⏳ Качаю: <b>{track['title']}</b>...")
    else:
        msg = await message.answer(f"⏩ Следующий: <b>{track['title']}</b>...")
    
    file_path, title, author = await download_track_fast(track['id'])
    
    await msg.delete()
    
    if file_path and os.path.exists(file_path):
        audio_file = FSInputFile(file_path)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏩ Следующий трек", callback_data="next_track")],
            [InlineKeyboardButton(text="⏹ Стоп / Меню", callback_data="game_music")]
        ])
        
        try:
            await message.answer_audio(
                audio=audio_file,
                title=title or track['title'],
                performer=author,
                caption=f"🎧 Вайб: {mood}",
                reply_markup=kb
            )
        except Exception as e:
            await message.answer("Ошибка отправки файла.")
        
        try: os.remove(file_path)
        except: pass
    else:
        await play_next_song(message, state, first_time=False)

# --- ПРАВДА ИЛИ ДЕЙСТВИЕ ---
@router.callback_query(F.data == "game_tod")
async def start_tod(callback: CallbackQuery):
    from keyboards.fun_kb import get_tod_kb
    if callback.message.audio:
        await callback.message.delete()
        await callback.message.answer("Выбирай: Правда или Действие?", reply_markup=get_tod_kb())
    else:
        await callback.message.edit_text("Выбирай: Правда или Действие?", reply_markup=get_tod_kb())

@router.callback_query(F.data.startswith("tod_"))
async def play_tod(callback: CallbackQuery):
    from keyboards.fun_kb import get_tod_kb
    choice = callback.data.split("_")[1]
    
    if choice == "truth":
        theme = random.choice(TRUTH_THEMES)
        prompt = (f"Придумай 1 вопрос для игры 'Правда или Действие' для девушки от её парня. "
                  f"Тема вопроса: {theme}. Вопрос должен быть интересным. Пиши ТОЛЬКО вопрос.")
    else:
        theme = random.choice(DARE_THEMES)
        prompt = (f"Придумай 1 задание (Действие) для игры 'Правда или Действие' для девушки. "
                  f"Тема задания: {theme}. Выполнимое сейчас. Без жести. Пиши ТОЛЬКО задание.")
    
    task = await get_ai_response(callback.from_user.id, prompt)
    text = f"🎲 <b>{choice.upper()}:</b>\n\n{task}"
    
    if callback.message.audio:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=get_tod_kb(), parse_mode="HTML")
    else:
        try: await callback.message.edit_text(text, reply_markup=get_tod_kb(), parse_mode="HTML")
        except: await callback.message.answer(text, reply_markup=get_tod_kb(), parse_mode="HTML")

# --- КУПОНЫ (ИСПРАВЛЕННАЯ ЛОГИКА) ---

@router.callback_query(F.data == "game_coupon")
async def get_coupon(callback: CallbackQuery):
    # Выбираем случайный ИНДЕКС
    coupon_index = random.randint(0, len(COUPONS) - 1)
    coupon_text = COUPONS[coupon_index]
    
    # В callback_data передаем ТОЛЬКО ИНДЕКС (use_coupon_5)
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Использовать сейчас", callback_data=f"use_coupon_{coupon_index}")],
        [InlineKeyboardButton(text="🎲 Вытянуть другой", callback_data="game_coupon")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_back")]
    ])
    
    text = f"🎟 <b>Твой Купон:</b>\n\n✨ {coupon_text} ✨"
    
    if callback.message.audio:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=markup, parse_mode="HTML")
    else:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

@router.callback_query(F.data.startswith("use_coupon_"))
async def activate_coupon(callback: CallbackQuery):
    # Получаем индекс и достаем полный текст из списка
    index = int(callback.data.split("_")[2])
    
    # Проверка на всякий случай
    if 0 <= index < len(COUPONS):
        full_text = COUPONS[index]
        
        await callback.bot.send_message(ADMIN_ID, f"🚨 <b>КУПОН АКТИВИРОВАН!</b>\n\nОна хочет: <b>{full_text}</b>\nБеги исполнять! 😉", parse_mode="HTML")
        await callback.answer("Активировано! ✅", show_alert=True)
        await callback.message.edit_text(f"✅ Купон «{full_text}» отправлен Жанарысу!")
    else:
        await callback.answer("Ошибка купона.", show_alert=True)

@router.callback_query(F.data == "game_back")
async def back_to_menu(callback: CallbackQuery):
    if callback.message.audio:
        await callback.message.delete()
        await callback.message.answer("Чем займемся? 😏", reply_markup=get_games_kb())
    else:
        await callback.message.edit_text("Чем займемся? 😏", reply_markup=get_games_kb())

@router.callback_query(F.data == "game_art")
async def art_info(callback: CallbackQuery):
    await callback.message.answer(
        "🎨 **Я умею рисовать!**\n\nПросто напиши мне в чат: <b>Нарисуй [что-то]</b>\nИли скинь фото с подписью.",
        parse_mode="HTML"
    )
    await callback.answer()