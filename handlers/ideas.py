from aiogram import Router, F
from aiogram.types import Message
from services.weather import get_weather_report
from services.gemini import get_ai_response

router = Router()

@router.message(F.text == "💡 Куда сходим?")
async def suggest_date(message: Message):
    # 1. Показываем, что бот думает
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # 2. Получаем погоду (техническую часть)
    # Мы используем 'current', чтобы узнать, что за окном прямо сейчас
    weather_text = await get_weather_report("current")
    
    # 3. Формируем запрос к Gemini
    prompt = (
        f"Мы с девушкой думаем, чем заняться. "
        f"Вот погода на улице: {weather_text}. "
        "Предложи 3 варианта свидания на сегодня, учитывая эту погоду:\n"
        "1. Ленивый вариант (дома или спокойное место).\n"
        "2. Активный вариант (прогулка или действие).\n"
        "3. Романтический вариант (ужин или атмосфера).\n"
        "Не пиши длинно. Пиши вкусно и с юмором. Обращайся к ней."
    )
    
    # 4. Получаем ответ
    response = await get_ai_response(message.from_user.id, prompt)
    
    await message.answer(f"🤔 <b>Анализирую погоду и настроение...</b>\n\n{response}", parse_mode="HTML")