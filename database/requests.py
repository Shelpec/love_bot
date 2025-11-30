from database.models import User, Compliment, Wish, Memory, Movie, Note, Cycle, Event, Savings, Place
from database.core import async_session
from sqlalchemy import select, delete, update
import random
from database.models import WordHistory 
from database.models import QuizAttempt
from datetime import date, datetime, timedelta # <-- ВОТ ЭТОГО НЕ ХВАТАЛО
# --- ЮЗЕРЫ ---
async def set_user(tg_id: int, name: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, name=name))
            await session.commit()

# --- КОМПЛИМЕНТЫ ---
async def get_random_compliment():
    async with async_session() as session:
        result = await session.execute(select(Compliment.text))
        compliments = result.scalars().all()
        if not compliments: return "Ты прекрасна!"
        return random.choice(compliments)

# --- ВИШЛИСТ ---
async def add_wish(tg_id: int, text: str | None, file_id: str | None, c_type: str):
    async with async_session() as session:
        session.add(Wish(tg_id=tg_id, wish_text=text, file_id=file_id, content_type=c_type))
        await session.commit()

async def get_all_wishes():
    async with async_session() as session:
        result = await session.execute(select(Wish))
        return result.scalars().all()

# --- ВОСПОМИНАНИЯ ---
async def add_memory(file_id: str, c_type: str, caption: str | None):
    async with async_session() as session:
        session.add(Memory(file_id=file_id, content_type=c_type, caption=caption))
        await session.commit()

async def get_random_memory():
    async with async_session() as session:
        result = await session.execute(select(Memory))
        memories = result.scalars().all()
        if not memories: return None
        return random.choice(memories)

# --- КИНО ---
async def add_movie(title: str, user_id: int):
    async with async_session() as session:
        session.add(Movie(title=title, added_by=user_id))
        await session.commit()

async def get_movies():
    async with async_session() as session:
        result = await session.execute(select(Movie))
        return result.scalars().all()

async def delete_movie(movie_id: int):
    async with async_session() as session:
        await session.execute(delete(Movie).where(Movie.id == movie_id))
        await session.commit()

# --- ЗАМЕТКИ ---
async def add_note(text: str):
    async with async_session() as session:
        session.add(Note(text=text))
        await session.commit()

async def get_notes():
    async with async_session() as session:
        result = await session.execute(select(Note))
        return result.scalars().all()

async def delete_note(note_id: int):
    async with async_session() as session:
        await session.execute(delete(Note).where(Note.id == note_id))
        await session.commit()

async def clear_notes():
    async with async_session() as session:
        await session.execute(delete(Note))
        await session.commit()

# --- ЦИКЛ ---
async def set_cycle(tg_id: int, start_date: date):
    async with async_session() as session:
        cycle = await session.scalar(select(Cycle).where(Cycle.tg_id == tg_id))
        if cycle:
            cycle.last_period_date = start_date
        else:
            session.add(Cycle(tg_id=tg_id, last_period_date=start_date))
        await session.commit()

async def get_cycle(tg_id: int):
    async with async_session() as session:
        return await session.scalar(select(Cycle).where(Cycle.tg_id == tg_id))

# --- СОБЫТИЯ (Вот этих функций не хватало!) ---
async def add_event(name: str, date_obj: date):
    async with async_session() as session:
        session.add(Event(name=name, event_date=date_obj))
        await session.commit()

async def get_today_events():
    today = date.today()
    async with async_session() as session:
        result = await session.execute(select(Event))
        events = result.scalars().all()
        todays = []
        for e in events:
            if e.event_date.day == today.day and e.event_date.month == today.month:
                todays.append(e.name)
        return todays

async def get_all_events():
    async with async_session() as session:
        result = await session.execute(select(Event))
        return result.scalars().all()
    
async def delete_event(event_id: int):
    async with async_session() as session:
        await session.execute(delete(Event).where(Event.id == event_id))
        await session.commit()



# --- АНГЛИЙСКИЙ (ИСТОРИЯ СЛОВ) ---
async def get_banned_words(tg_id: int):
    async with async_session() as session:
        subq = select(WordHistory.word).where(WordHistory.tg_id == tg_id).order_by(WordHistory.last_seen.desc()).limit(25)
        result_recent = await session.execute(subq)
        recent_words = [row for row in result_recent.scalars().all()]
        
        subq2 = select(WordHistory.word).where(WordHistory.tg_id == tg_id).where(WordHistory.count >= 5)
        result_learned = await session.execute(subq2)
        learned_words = [row for row in result_learned.scalars().all()]
        
        return list(set(recent_words + learned_words))

async def update_word_stat(tg_id: int, word: str):
    word = word.lower().strip()
    async with async_session() as session:
        record = await session.scalar(select(WordHistory).where(WordHistory.tg_id == tg_id, WordHistory.word == word))
        if record:
            record.count += 1
            record.last_seen = func.now()
        else:
            session.add(WordHistory(tg_id=tg_id, word=word, count=1))
        await session.commit()



# --- АНГЛИЙСКИЙ (СТАТИСТИКА ОТВЕТОВ) ---
async def log_quiz_attempt(tg_id: int, is_correct: bool):
    async with async_session() as session:
        session.add(QuizAttempt(tg_id=tg_id, is_correct=is_correct))
        await session.commit()

async def get_quiz_stats(tg_id: int):
    # Теперь datetime импортирован, ошибки не будет
    now = datetime.now()
    
    periods = {
        "day": now - timedelta(days=1),
        "week": now - timedelta(weeks=1),
        "month": now - timedelta(days=30)
    }
    
    stats = {}
    
    async with async_session() as session:
        for period_name, date_limit in periods.items():
            query = select(QuizAttempt).where(
                QuizAttempt.tg_id == tg_id,
                QuizAttempt.timestamp >= date_limit
            )
            result = await session.execute(query)
            attempts = result.scalars().all()
            
            total = len(attempts)
            correct = sum(1 for a in attempts if a.is_correct)
            
            stats[period_name] = {
                "total": total,
                "correct": correct,
                "percent": int((correct / total) * 100) if total > 0 else 0
            }
            
    return stats




# --- КОПИЛКА ---
async def get_savings():
    async with async_session() as session:
        # Берем первую цель (предполагаем, что копим на что-то одно глобальное)
        return await session.scalar(select(Savings))

async def set_savings_goal(name: str, target: int):
    async with async_session() as session:
        # Удаляем старую, создаем новую
        await session.execute(delete(Savings))
        session.add(Savings(goal_name=name, target_amount=target, current_amount=0))
        await session.commit()

async def add_money(amount: int):
    async with async_session() as session:
        saving = await session.scalar(select(Savings))
        if saving:
            saving.current_amount += amount
            await session.commit()
            return saving
        return None

# --- КАРТА МЕСТ ---
async def add_place(name: str, lat: float, lon: float, user_id: int):
    async with async_session() as session:
        session.add(Place(name=name, latitude=lat, longitude=lon, added_by=user_id))
        await session.commit()

async def get_all_places():
    async with async_session() as session:
        result = await session.execute(select(Place))
        return result.scalars().all()

async def delete_place(place_id: int):
    async with async_session() as session:
        await session.execute(delete(Place).where(Place.id == place_id))
        await session.commit()