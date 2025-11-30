from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database.requests as rq

router = Router()

class MapState(StatesGroup):
    waiting_for_name = State()

# --- МЕНЮ КАРТЫ ---
@router.message(F.text == "📍 Карта Наших Мест")
async def show_map_menu(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺 Показать список мест", callback_data="places_list")],
        [InlineKeyboardButton(text="📍 Добавить новое место", callback_data="places_add")]
    ])
    await message.answer(
        "Это карта вашей любви в Астане! 🇰🇿❤️\n"
        "Здесь хранятся ваши любимые локации.", 
        reply_markup=kb
    )

# --- ДОБАВЛЕНИЕ МЕСТА ---
@router.callback_query(F.data == "places_add")
async def start_add_place(callback: CallbackQuery):
    await callback.message.answer(
        "📍 <b>Как добавить место:</b>\n\n"
        "1. Нажми на скрепку (📎) внизу.\n"
        "2. Выбери 'Геопозиция' (Location).\n"
        "3. Отправь точку на карте."
    , parse_mode="HTML")
    await callback.answer()

# Ловим геолокацию
@router.message(F.content_type == "location")
async def handle_location(message: Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    
    # Запоминаем координаты
    await state.update_data(lat=lat, lon=lon)
    await state.set_state(MapState.waiting_for_name)
    
    await message.answer("Супер! Как назовем это место? (Например: 'Наше кафе')")

@router.message(MapState.waiting_for_name)
async def save_place_name(message: Message, state: FSMContext):
    data = await state.get_data()
    name = message.text
    
    await rq.add_place(name, data['lat'], data['lon'], message.from_user.id)
    await message.answer(f"✅ Место <b>«{name}»</b> сохранено на карте!", parse_mode="HTML")
    await state.clear()

# --- СПИСОК МЕСТ ---
@router.callback_query(F.data == "places_list")
async def list_places(callback: CallbackQuery):
    places = await rq.get_all_places()
    
    if not places:
        await callback.answer("Список пуст! Добавь что-нибудь.", show_alert=True)
        return

    await callback.message.delete() # Чистим меню
    
    for place in places:
        # Генерируем ссылку для 2ГИС
        # Формат: https://2gis.kz/geo/LONGITUDE,LATITUDE
        gis_url = f"https://2gis.kz/geo/{place.longitude},{place.latitude}"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗺 Открыть в 2GIS", url=gis_url)],
            [InlineKeyboardButton(text="❌ Удалить", callback_data=f"del_place_{place.id}")]
        ])
        
        # Отправляем точку (чтобы было видно на карте в телеге)
        await callback.message.answer_location(
            latitude=place.latitude, 
            longitude=place.longitude
        )
        # И описание с кнопкой
        await callback.message.answer(
            f"📍 <b>{place.name}</b>", 
            reply_markup=kb, 
            parse_mode="HTML"
        )
    
    # Кнопка возврата
    kb_back = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню карты", callback_data="map_back")]])
    await callback.message.answer("Вот ваши места 👆", reply_markup=kb_back)

@router.callback_query(F.data.startswith("del_place_"))
async def delete_place_handler(callback: CallbackQuery):
    p_id = int(callback.data.split("_")[2])
    await rq.delete_place(p_id)
    await callback.answer("Место удалено.")
    # Можно удалить сообщение, но это сложно с location, просто уведомим

@router.callback_query(F.data == "map_back")
async def back_to_map(callback: CallbackQuery):
    await show_map_menu(callback.message)