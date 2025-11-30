from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from services.painter import generate_image
from services.gemini import get_image_description
import os

router = Router()

# 1. ГЕНЕРАЦИЯ ПО ТЕКСТУ ("Нарисуй кота")
@router.message(F.text.lower().startswith("нарисуй"))
async def draw_picture(message: Message):
    user_prompt = message.text[7:].strip()
    
    if not user_prompt:
        await message.answer("А что нарисовать? Пример: <i>Нарисуй кота в космосе</i>", parse_mode="HTML")
        return

    await process_generation(message, user_prompt)

# 2. ГЕНЕРАЦИЯ ПО ФОТО (Перерисовка)
@router.message(F.photo)
async def redraw_photo(message: Message):
    # Проверяем, есть ли подпись (стиль)
    # Например: скинула фото и подписала "В стиле аниме"
    user_style = message.caption
    
    if not user_style:
        # Если подписи нет, просто игнорируем (вдруг она просто фото скинула для сохранения)
        # Или можно предложить нарисовать. Но пока просто выйдем.
        return 

    # Если в подписи есть слово "нарисуй" или просто стиль
    if "нарисуй" in user_style.lower() or len(user_style) > 0:
        await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
        status = await message.answer("👀 <b>Смотрю на фото и придумываю образ...</b>", parse_mode="HTML")
        
        # 1. Скачиваем фото
        photo = message.photo[-1]
        file_path = f"downloads/{photo.file_id}.jpg"
        
        # Создаем папку если нет
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
            
        await message.bot.download(photo, destination=file_path)
        
        try:
            # 2. Gemini описывает фото + стиль
            description_prompt = await get_image_description(file_path, user_style)
            
            if not description_prompt:
                await status.edit_text("Не удалось распознать фото...")
                return
            
            await status.edit_text(f"🎨 <b>Рисую по фото...</b>\n<i>Стиль: {user_style}</i>", parse_mode="HTML")
            
            # 3. Генерируем картинку по описанию
            # (Функция generate_image у нас уже есть, она сама скачивает байты)
            image_bytes, final_prompt = await generate_image(description_prompt)
            
            # 4. Отправляем
            photo_file = BufferedInputFile(image_bytes, filename="art.png")
            await message.answer_photo(
                photo=photo_file,
                caption=f"🖼 <b>Готово!</b>\n🎭 <i>Оригинал + {user_style}</i>",
                parse_mode="HTML"
            )
            await status.delete()

        except Exception as e:
            await status.edit_text(f"Ошибка художника: {e}")
        
        finally:
            # Удаляем временный файл
            if os.path.exists(file_path):
                os.remove(file_path)

# --- ОБЩАЯ ФУНКЦИЯ ДЛЯ ОТПРАВКИ (чтобы не дублировать код) ---
async def process_generation(message: Message, prompt: str):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
    status_msg = await message.answer(f"🎨 <b>Смешиваю краски...</b>\n<i>Запрос: {prompt}</i>", parse_mode="HTML")
    
    try:
        image_bytes, prompt_en = await generate_image(prompt)
        photo_file = BufferedInputFile(image_bytes, filename="image.png")
        
        await message.answer_photo(
            photo=photo_file,
            caption=f"🖼 <b>Готово!</b>",
            parse_mode="HTML"
        )
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(f"Ошибка: {e}")