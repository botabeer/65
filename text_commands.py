import random
import os

class TextCommands:
    _data = {}       # جميع البيانات لكل ملف
    _remaining = {}  # العناصر المتبقية للاختيار بدون تكرار
    _files = {
        'questions': 'games/questions.txt',
        'challenges': 'games/challenges.txt',
        'confessions': 'games/confessions.txt',
        'mentions': 'games/mentions.txt',
        'quotes': 'games/quotes.txt',
        'situations': 'games/situations.txt',
        'private': 'games/private.txt',
        'anonymous': 'games/anonymous.txt',
        'advice': 'games/advice.txt'
    }
    
    @classmethod
    def load_all(cls):
        """تحميل كل الملفات وتخزينها في _data وتهيئة _remaining."""
        for key, path in cls._files.items():
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        lines = [line.strip() for line in f if line.strip()]
                        cls._data[key] = lines
                else:
                    cls._data[key] = [f"المحتوى غير متوفر لـ {key}"]
                cls._remaining[key] = cls._data[key].copy()
            except Exception as e:
                cls._data[key] = [f"خطأ في تحميل {key}"]
                cls._remaining[key] = cls._data[key].copy()
    
    @classmethod
    def get_random(cls, cmd):
        """إرجاع عنصر عشوائي بدون تكرار حتى تنفد القائمة."""
        if not cls._data:
            cls.load_all()
        
        if cmd not in cls._data:
            return "لا يوجد محتوى"
        
        # إذا فرغت العناصر المتبقية، إعادة نسخة من البيانات الأصلية
        if not cls._remaining.get(cmd):
            cls._remaining[cmd] = cls._data[cmd].copy()
        
        choice = random.choice(cls._remaining[cmd])
        cls._remaining[cmd].remove(choice)  # إزالة العنصر لضمان عدم تكراره
        
        return choice
