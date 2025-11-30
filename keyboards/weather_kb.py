from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

def get_weather_keyboard():
    builder = InlineKeyboardBuilder()
    now_hour = datetime.now().hour

    # 1. Кнопка "Сейчас" (Всегда)
    builder.row(InlineKeyboardButton(text="📍 Сейчас", callback_data="weather_current"))
    
    # 2. Кнопка "Через час" (Всегда)
    builder.add(InlineKeyboardButton(text="⏱ Через час", callback_data="weather_plus_1"))

    # 3. Кнопка "Сегодня Обед" (Только если еще не прошло 14:00)
    if now_hour < 14:
        builder.row(InlineKeyboardButton(text="🍲 Сегодня в обед", callback_data="weather_today_lunch"))

    # 4. Кнопка "Сегодня Вечер" (Только если еще не прошло 20:00)
    if now_hour < 20:
        # Если кнопка обеда была, добавляем рядом, если нет - новой строкой
        if now_hour < 14:
            builder.add(InlineKeyboardButton(text="🌙 Сегодня вечером", callback_data="weather_today_evening"))
        else:
            builder.row(InlineKeyboardButton(text="🌙 Сегодня вечером", callback_data="weather_today_evening"))

    # 5. Кнопка "Завтра утром" (Всегда)
    builder.row(InlineKeyboardButton(text="🌅 Завтра утром", callback_data="weather_tomorrow_morning"))

    return builder.as_markup()