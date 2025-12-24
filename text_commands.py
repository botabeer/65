import random
import os

class TextCommands:
    _data = {}
    _files = {
        'questions': 'games/questions.txt',
        'challenges': 'games/challenges.txt',
        'confessions': 'games/confessions.txt',
        'mentions': 'games/mentions.txt',
        'quotes': 'games/quotes.txt',
        'situations': 'games/situations.txt'
    }
    
    @classmethod
    def load_all(cls):
        for key, path in cls._files.items():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    cls._data[key] = [line.strip() for line in f if line.strip()]
            except:
                cls._data[key] = [f"المحتوى غير متوفر"]
    
    @classmethod
    def get_random(cls, cmd):
        if not cls._data:
            cls.load_all()
        return random.choice(cls._data.get(cmd, ["غير متوفر"]))
