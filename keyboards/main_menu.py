from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        # 1 ряд
        [
            KeyboardButton(text="❤️ Наши воспоминания"),
            KeyboardButton(text="💌 Комплимент"),
        ],
        [
            KeyboardButton(text="💰 Семейная Копилка"), # <-- Новая
            KeyboardButton(text="📍 Карта Наших Мест"), # <-- Новая
        ],
        # 2 ряд
        [
            KeyboardButton(text="🌦 Погода и Забота"),
            KeyboardButton(text="💡 Куда сходим?"),
            KeyboardButton(text="🇬🇧 Учить английский"), 
        ],
        # 3 ряд: ИГРЫ (Добавили сюда)
        [
            KeyboardButton(text="🎁 Хочу подарок"),
            KeyboardButton(text="🎲 Игры для нас"), 
            KeyboardButton(text="📝 Общие заметки"), # <-- Новая
        ],
        # 4 ряд
        [
            KeyboardButton(text="🔮 Магия и Таро"),
            KeyboardButton(text="🆘 МНЕ ГРУСТНО"),
        ],
        # 5 ряд
        [
            KeyboardButton(text="🎬 Кино-Комната"),
            KeyboardButton(text="🧠 Поболтать с ИИ"),
            KeyboardButton(text="🌸 Мой цикл"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Люблю тебя..."
)