import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

from config import BOT_TOKEN
from database.core import async_main, async_session
from database.models import User
from sqlalchemy import select

# Импорты хэндлеров
from handlers import start, romance, utility, ai_chat, wishlist, magic, admin, ideas, fun, cinema, art, reminders, care, english, finance, map
from services.morning import morning_routine

logging.basicConfig(level=logging.INFO)

async def main():
    await async_main()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    scheduler = AsyncIOScheduler()
    
    # --- НАСТРОЙКА ВРЕМЕНИ ---
    # Для теста: посмотри на часы на компьютере.
    # Если сейчас 21:15, поставь здесь 21:17, запусти и жди.
    scheduler.add_job(morning_routine, 'cron', hour=21, minute=16, args=[bot])
    
    # Для реальной работы потом поменяешь на: hour=8, minute=0
    
    scheduler.start()
    dp["scheduler"] = scheduler

    # Подключаем роутеры
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(finance.router) 
    dp.include_router(map.router)     
    dp.include_router(care.router)
    dp.include_router(english.router) 
    dp.include_router(reminders.router)
    dp.include_router(wishlist.router)
    dp.include_router(magic.router)
    dp.include_router(romance.router)
    dp.include_router(cinema.router)
    dp.include_router(utility.router)
    dp.include_router(ideas.router)
    dp.include_router(fun.router)
    dp.include_router(art.router)
    
    dp.include_router(ai_chat.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")