from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models import Base

# Создаем файл db.sqlite3 в корне проекта
engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3", echo=True)

# Фабрика сессий (через нее мы будем делать запросы)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Функция создания таблиц (запустим один раз при старте)
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)