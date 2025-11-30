import aiohttp
from config import WEATHER_KEY, CITY
from services.gemini import get_ai_response
from datetime import datetime, timedelta

BASE_URL = "http://api.openweathermap.org/data/2.5"

async def get_weather_json(endpoint: str):
    url = f"{BASE_URL}/{endpoint}?q={CITY}&appid={WEATHER_KEY}&units=metric&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            return await resp.json()

# Получение детального прогноза
async def get_weather_report(request_type: str):
    """
    request_type: 'current', 'plus_1', 'today_lunch', 'today_evening', 'tomorrow_morning'
    """
    
    # 1. Если просят "Прямо сейчас"
    if request_type == 'current':
        data = await get_weather_json("weather")
        if not data: return "Ошибка связи с метеоцентром."
        
        # Собираем данные
        temp = round(data["main"]["temp"], 1)
        feels = round(data["main"]["feels_like"], 1)
        desc = data["weather"][0]["description"]
        wind = data["wind"]["speed"]
        humidity = data["main"]["humidity"]
        
        time_desc = "прямо сейчас"
        
    # 2. Если просят прогноз (из списка на 5 дней)
    else:
        data = await get_weather_json("forecast")
        if not data: return "Ошибка получения прогноза."
        
        now = datetime.now()
        target_time = now
        time_desc = ""

        # Определяем целевое время
        if request_type == 'plus_1':
            target_time = now + timedelta(hours=1)
            time_desc = "через час"
        elif request_type == 'today_lunch':
            target_time = now.replace(hour=13, minute=0, second=0, microsecond=0)
            time_desc = "сегодня в обед"
        elif request_type == 'today_evening':
            target_time = now.replace(hour=19, minute=0, second=0, microsecond=0)
            time_desc = "сегодня вечером"
        elif request_type == 'tomorrow_morning':
            target_time = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
            time_desc = "завтра утром"

        # Ищем ближайший прогноз в списке
        closest_item = None
        min_diff = float('inf')

        for item in data['list']:
            item_dt = datetime.fromtimestamp(item['dt'])
            diff = abs((item_dt - target_time).total_seconds())
            
            if diff < min_diff:
                min_diff = diff
                closest_item = item
        
        if not closest_item:
            return "Не удалось найти прогноз на это время."

        # Данные из прогноза
        temp = round(closest_item["main"]["temp"], 1)
        feels = round(closest_item["main"]["feels_like"], 1)
        desc = closest_item["weather"][0]["description"]
        wind = closest_item["wind"]["speed"]
        humidity = closest_item["main"]["humidity"]
        # Вероятность осадков (если есть поле pop)
        pop = int(closest_item.get("pop", 0) * 100) 
        rain_prob = f", вероятность осадков {pop}%" if pop > 0 else ""

    # --- ФОРМИРОВАНИЕ ОТЧЕТА ---
    
    # Техническая строка со всеми деталями
    tech_report = (
        f"Прогноз {time_desc} в {CITY}:\n"
        f"- Состояние: {desc}\n"
        f"- Температура: {temp}°C (ощущается как {feels}°C)\n"
        f"- Ветер: {wind} м/с\n"
        f"- Влажность: {humidity}%"
    )
    if 'rain_prob' in locals():
        tech_report += rain_prob

    # Промпт для Джарвиса
    prompt = (
        f"Вот точные данные о погоде: {tech_report}. "
        "Твоя задача: Рассказать об этом девушке. "
        "ОБЯЗАТЕЛЬНО укажи цифры (градусы и ветер), это важно для неё. "
        "Если есть дождь, снег или ветер — предупреди. "
        "Дай короткий совет по одежде. Будь заботлив, как дворецкий."
    )

    return await get_ai_response(0, prompt)