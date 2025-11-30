from sqlalchemy import BigInteger, String, DateTime, func, Integer, Date, Boolean, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, date

class Base(DeclarativeBase):
    pass

# --- СТАРЫЕ ТАБЛИЦЫ (Оставляем) ---
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class Compliment(Base):
    __tablename__ = 'compliments'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String)

class Wish(Base):
    __tablename__ = 'wishes'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    wish_text: Mapped[str] = mapped_column(String, nullable=True) 
    file_id: Mapped[str] = mapped_column(String, nullable=True)
    content_type: Mapped[str] = mapped_column(String, default="text")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class Memory(Base):
    __tablename__ = 'memories'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(String)
    content_type: Mapped[str] = mapped_column(String)
    caption: Mapped[str] = mapped_column(String, nullable=True)

class Movie(Base):
    __tablename__ = 'movies'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    added_by: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class Note(Base):
    __tablename__ = 'notes'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class Cycle(Base):
    __tablename__ = 'cycle'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    last_period_date: Mapped[date] = mapped_column(Date)
    cycle_length: Mapped[int] = mapped_column(Integer, default=28)

class Event(Base):
    __tablename__ = 'events'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    event_date: Mapped[date] = mapped_column(Date)
    is_annual: Mapped[bool] = mapped_column(Integer, default=1)

class WordHistory(Base):
    __tablename__ = 'word_history'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    word: Mapped[str] = mapped_column(String)
    count: Mapped[int] = mapped_column(Integer, default=1)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class QuizAttempt(Base):
    __tablename__ = 'quiz_attempts'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())

# --- НОВЫЕ ТАБЛИЦЫ ---

# Копилка
class Savings(Base):
    __tablename__ = 'savings'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    goal_name: Mapped[str] = mapped_column(String) # Название цели (Мальдивы)
    target_amount: Mapped[int] = mapped_column(Integer) # Сколько нужно (1000000)
    current_amount: Mapped[int] = mapped_column(Integer, default=0) # Сколько есть

# Места (Карта)
class Place(Base):
    __tablename__ = 'places'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String) # "Наш парк"
    latitude: Mapped[float] = mapped_column(Float) # Широта
    longitude: Mapped[float] = mapped_column(Float) # Долгота
    added_by: Mapped[int] = mapped_column(BigInteger)