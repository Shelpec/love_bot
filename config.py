import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
GEMINI_KEY = os.getenv("GEMINI_KEY") 
WEATHER_KEY = os.getenv("WEATHER_KEY")
CITY = os.getenv("CITY")