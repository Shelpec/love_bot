import random

MUSIC_DATABASE = {
    "sad": [
        "https://www.youtube.com/watch?v=4N3N1MlvVc4", # Mad World
        "https://www.youtube.com/watch?v=YQHsXMglC9A", # Hello
        "https://www.youtube.com/watch?v=rbqK28i7dKk", # Tom Odell - Another Love
    ],
    "love": [
        "https://www.youtube.com/watch?v=rtOvBOTyX00", # Ed Sheeran - Perfect
        "https://www.youtube.com/watch?v=lp-EO5I60KA", # Ed Sheeran - Thinking Out Loud
        "https://www.youtube.com/watch?v=2Vv-BfVoq4g", # Ed Sheeran - Perfect
    ],
    "party": [
        "https://www.youtube.com/watch?v=09R8_2nJtjg", # Sugar
        "https://www.youtube.com/watch?v=OPf0YbXqDm0", # Uptown Funk
        "https://www.youtube.com/watch?v=JGwWNGJdvx8", # Shape of You
    ]
}

def get_music_by_mood(mood: str):
    if mood in MUSIC_DATABASE:
        return random.choice(MUSIC_DATABASE[mood])
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"