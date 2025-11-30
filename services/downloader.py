import yt_dlp
import os
import asyncio

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# 1. ПОИСК ПАЧКОЙ (Надежный метод)
async def search_batch(query: str, limit: int = 15):
    ydl_opts = {
        'quiet': True,
        'default_search': f'ytsearch{limit}', # Ищем N треков
        'noplaylist': True,
        'ignoreerrors': True,
        'no_warnings': True,
        # Убрали extract_flat, так как он иногда возвращает пустоту
    }

    try:
        loop = asyncio.get_event_loop()
        # Добавляем "audio" к запросу для точности
        search_query = f"{query} audio"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(search_query, download=False))
            
            tracks = []
            if 'entries' in info:
                for entry in info['entries']:
                    if not entry: continue
                    
                    # Фильтруем слишком длинные (больше 15 мин) и слишком короткие
                    duration = entry.get('duration', 0)
                    if duration < 60 or duration > 900: continue

                    tracks.append({
                        'id': entry['id'],
                        'title': entry.get('title', 'Трек'),
                        'author': entry.get('uploader', 'Music')
                    })
            return tracks
            
    except Exception as e:
        print(f"Ошибка поиска: {e}")
        return []

# 2. СКАЧИВАНИЕ (Быстрое)
async def download_track_fast(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        # Качаем m4a (самый легкий и быстрый формат)
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }

    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)
            
            # Проверка расширения (иногда yt-dlp меняет его)
            base, ext = os.path.splitext(filename)
            if not os.path.exists(filename):
                for check_ext in ['.m4a', '.webm', '.mp3', '.mkv']:
                    if os.path.exists(base + check_ext):
                        filename = base + check_ext
                        break
            
            return filename, info.get('title'), info.get('uploader')
            
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return None, None, None