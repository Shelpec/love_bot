from gtts import gTTS
import os

def text_to_speech_file(text: str, filename: str):
    # gTTS создает mp3
    tts = gTTS(text, lang='ru')
    path = f"downloads/{filename}.mp3"
    
    # Создаем папку если нет
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
        
    tts.save(path)
    return path