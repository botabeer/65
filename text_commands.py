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
        'situations': 'games/situations.txt',
        'poem': 'games/poem.txt',
        'private': 'games/private.txt',
        'anonymous': 'games/anonymous.txt',
        'advice': 'games/advice.txt'
    }
    
    @classmethod
    def load_all(cls):
        for key, path in cls._files.items():
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        cls._data[key] = [line.strip() for line in f if line.strip()]
                else:
                    cls._data[key] = [f"المحتوى غير متوفر لـ {key}"]
            except Exception as e:
                cls._data[key] = [f"خطأ في تحميل {key}"]
    
    @classmethod
    def get_random(cls, cmd):
        if not cls._data:
            cls.load_all()
        items = cls._data.get(cmd, ["غير متوفر"])
        if not items:
            return "لا يوجد محتوى"
        return random.choice(items)
