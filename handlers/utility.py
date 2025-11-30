from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.weather_kb import get_weather_keyboard # <-- Импорт функции
from services.weather import get_weather_report

router = Router()

# Показываем меню погоды
@router.message(F.text == "🌦 Погода и Забота")
async def show_weather_options(message: Message):
    # Генерируем клавиатуру в зависимости от времени суток
    kb = get_weather_keyboard()
    
    await message.answer(
        "На какое время узнать погоду, мэм? 🧐", 
        reply_markup=kb
    )

# Обработка нажатий
@router.callback_query(F.data.startswith("weather_"))
async def send_weather_report(callback: CallbackQuery):
    request_type = callback.data.split("_", 1)[1] # Получаем все после weather_
    
    await callback.answer("Получаю данные со спутника...")
    
    # Генерируем отчет
    text = await get_weather_report(request_type)
    
    await callback.message.answer(text)