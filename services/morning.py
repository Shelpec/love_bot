from datetime import datetime, timedelta
from aiogram import Bot
from database.core import async_session
from database.models import User
from sqlalchemy import select
import database.requests as rq
from services.weather import get_weather_report
from services.gemini import get_ai_response
from config import ADMIN_ID

async def morning_routine(bot: Bot):
    print("☀️ Запуск утренней рассылки...") # Лог в консоль
    
    # 1. Получаем данные
    weather = await get_weather_report("current")
    horoscope = await get_ai_response(0, "Короткий и милый гороскоп на сегодня для девушки (Знак Дева).")
    events = await rq.get_today_events()
    
    # 2. Текст сообщения
    text_for_her = (
        f"<b>Доброе утро, моя принцесса! ☀️</b>\n\n"
        f"🌡 <b>За окном:</b>\n{weather}\n\n"
        f"✨ <b>Звезды шепчут:</b>\n{horoscope}\n\n"
    )
    
    if events:
        text_for_her += f"🎉 <b>СЕГОДНЯ ПРАЗДНИК!</b>\n{' '.join(events)}! Поздравляю! 🥳\n\n"
    
    text_for_her += "Желаю тебе чудесного дня! Люблю! ❤️"

    # 3. Отправляем ВСЕМ пользователям (и тебе, и ей)
    her_id = None
    
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("⚠️ В базе нет пользователей!")
            return

        for user in users:
            # Запоминаем ID девушки (любой, кто не админ) для проверки цикла
            if user.tg_id != ADMIN_ID:
                her_id = user.tg_id
            
            # Отправляем сообщение КАЖДОМУ (чтобы ты тоже видел)
            try:
                await bot.send_message(chat_id=user.tg_id, text=text_for_her, parse_mode="HTML")
                print(f"✅ Отправлено юзеру {user.tg_id}")
            except Exception as e:
                print(f"❌ Ошибка отправки юзеру {user.tg_id}: {e}")

    # 4. ПРОВЕРКА ЦИКЛА (Уведомление только ТЕБЕ)
    # Если в базе только ты, этот блок пропустится (и это нормально)
    if her_id:
        cycle = await rq.get_cycle(her_id)
        if cycle:
            today = datetime.now().date()
            last = cycle.last_period_date
            length = cycle.cycle_length
            
            next_period = last + timedelta(days=length)
            pms_start = next_period - timedelta(days=5)
            
            admin_alert = ""
            if today == pms_start:
                admin_alert = "🚨 <b>ВНИМАНИЕ! ПМС!</b>\nКупи шоколадку и будь терпелив. Это началось. 🍫"
            elif today == next_period:
                admin_alert = "🩸 <b>Календарь:</b>\nСегодня ожидается начало цикла."
                
            if admin_alert:
                try:
                    await bot.send_message(chat_id=ADMIN_ID, text=admin_alert, parse_mode="HTML")
                except: pass