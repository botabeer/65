import random
import os

class TextCommands:
    _data = {}
    _remaining = {}  # لتتبع العناصر المتبقية لكل فئة
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
                # عند التحميل، نهيئ قائمة العناصر المتبقية
                cls._remaining[key] = cls._data[key].copy()
            except Exception as e:
                cls._data[key] = [f"خطأ في تحميل {key}"]
                cls._remaining[key] = cls._data[key].copy()
    
    @classmethod
    def get_random(cls, cmd):
        if not cls._data:
            cls.load_all()
        
        # إذا فئة غير موجودة
        if cmd not in cls._data:
            return "لا يوجد محتوى"
        
        # إعادة تعبئة العناصر المتبقية إذا انتهت
        if not cls._remaining.get(cmd):
            cls._remaining[cmd] = cls._data[cmd].copy()
        
        # اختيار عنصر عشوائي من العناصر المتبقية
        choice = random.choice(cls._remaining[cmd])
        cls._remaining[cmd].remove(choice)  # إزالة لمنع التكرار
        
        return choice
