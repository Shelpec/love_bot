from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_games_kb():
    builder = InlineKeyboardBuilder()
    
    # 1. Правда или Действие
    builder.row(InlineKeyboardButton(text="😈 Правда или Действие", callback_data="game_tod"))
    
    # 2. Купоны
    builder.row(InlineKeyboardButton(text="🎟 Получить Купон", callback_data="game_coupon"))

    
    builder.row(InlineKeyboardButton(text="🎨 Нейро-Художник", callback_data="game_art"))
    
    # 3. МУЗЫКА (Новая кнопка)
    builder.row(InlineKeyboardButton(text="🎧 Музыка под настроение", callback_data="game_music"))
    
    return builder.as_markup()

def get_tod_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗣 Правда", callback_data="tod_truth"),
            InlineKeyboardButton(text="🔥 Действие", callback_data="tod_dare")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_back")]
    ])

def get_coupon_kb(coupon_name):
    short_name = coupon_name[:20]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Использовать сейчас", callback_data=f"use_coupon_{short_name}")],
        [InlineKeyboardButton(text="🎲 Вытянуть другой", callback_data="game_coupon")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="game_back")]
    ])