from aiogram import Router, F, Bot
from aiogram.types import Message
from services.gemini import parse_reminder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

router = Router()

# Нам нужен доступ к шедулеру, который мы создали в main.py
# Чтобы не усложнять архитектуру передачей объекта, мы создадим локальную функцию добавления
# (Но правильнее в больших проектах использовать Middleware, здесь упростим)

# Хак: мы будем добавлять задачу в тот же шедулер, который работает в main
# Для этого нам нужно, чтобы main передал нам его.
# Но пока сделаем проще: будем использовать глобальный список задач или передадим bot в функцию.

# --- ФУНКЦИЯ ОТПРАВКИ НАПОМИНАНИЯ ---
async def send_reminder_job(bot: Bot, chat_id: int, text: str):
    try:
        await bot.send_message(chat_id, f"🔔 <b>Напоминание:</b>\n\n{text}")
    except Exception as e:
        print(f"Не удалось отправить напоминание: {e}")

# --- ОБРАБОТЧИК ---
@router.message(F.text.lower().startswith("напомни"))
async def set_reminder(message: Message, bot: Bot, scheduler: AsyncIOScheduler): 
    # ^^^ ВАЖНО: Мы добавили аргумент scheduler (нужно будет настроить в main.py)
    
    user_text = message.text
    
    status = await message.answer("⏳ <b>Записываю...</b>", parse_mode="HTML")
    
    # 1. Парсим время через Gemini
    target_date, task_text = await parse_reminder(user_text)
    
    if not target_date:
        await status.edit_text("Не понял, на какое время поставить? 🤷‍♂️\nНапиши, например: <i>Напомни через 15 минут выпить воды</i>")
        return
    
    # Проверка, что время в будущем
    if target_date < datetime.now():
        await status.edit_text("Это время уже прошло! 😅")
        return

    # 2. Ставим задачу в планировщик
    scheduler.add_job(
        send_reminder_job,
        'date',
        run_date=target_date,
        kwargs={'bot': bot, 'chat_id': message.chat.id, 'text': task_text}
    )
    
    # Красивый вывод времени
    time_str = target_date.strftime("%H:%M")
    date_str = target_date.strftime("%d.%m")
    
    await status.edit_text(
        f"✅ <b>Готово!</b>\n\n"
        f"📌 Задача: <i>{task_text}</i>\n"
        f"⏰ Время: <b>{time_str}</b> ({date_str})"
    , parse_mode="HTML")