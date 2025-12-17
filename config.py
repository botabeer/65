import os
import re
from dotenv import load_dotenv

load_dotenv()

class Config:
    LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    DB_PATH = os.getenv("DB_PATH", "botmesh.db")
    PORT = int(os.getenv("PORT", 5000))
    WORKERS = int(os.getenv("WORKERS", 4))
    ENV = os.getenv("ENV", "production")
    
    QUESTIONS_PER_GAME = 5
    MAX_NAME_LENGTH = 50
    MIN_NAME_LENGTH = 1
    
    DAILY_REWARD_POINTS = 10
    DAILY_REWARD_HOURS = 24
    
    ACHIEVEMENTS = {
        "first_game": {"name": "اللعبة الأولى", "desc": "أكمل أول لعبة", "points": 5},
        "ten_games": {"name": "محترف", "desc": "أكمل 10 ألعاب", "points": 20},
        "fifty_games": {"name": "خبير", "desc": "أكمل 50 لعبة", "points": 50},
        "hundred_games": {"name": "أسطورة", "desc": "أكمل 100 لعبة", "points": 100},
        "first_win": {"name": "الفوز الأول", "desc": "احصل على فوز مثالي", "points": 10},
        "ten_wins": {"name": "فائز متميز", "desc": "احصل على 10 انتصارات", "points": 30},
        "hundred_points": {"name": "جامع النقاط", "desc": "اجمع 100 نقطة", "points": 25},
        "streak_3": {"name": "سلسلة قوية", "desc": "فز بـ 3 ألعاب متتالية", "points": 15},
        "streak_5": {"name": "سلسلة ذهبية", "desc": "فز بـ 5 ألعاب متتالية", "points": 35},
        "all_games": {"name": "المستكشف", "desc": "جرب جميع الألعاب", "points": 40}
    }
    
    RESERVED_COMMANDS = {
        "بدايه", "بداية", "العاب", "نقاطي", "الصداره", "الصدارة",
        "ثيم", "مساعده", "مساعدة", "تسجيل", "ايقاف", "إيقاف", "انسحب",
        "ذكاء", "خمن", "رياضيات", "ترتيب", "ضد", "اضداد", "كتابه",
        "كتابة", "سلسله", "سلسلة", "انسان", "إنسان", "حيوان", "كلمات",
        "اغنيه", "أغنية", "الوان", "ألوان", "توافق", "مافيا",
        "تحدي", "اعتراف", "منشن", "شخصيه", "شخصية", "سؤال",
        "حكمه", "حكمة", "موقف", "مكافأة", "مكافاة", "انجازات", "إنجازات"
    }
    
    @staticmethod
    def normalize(text):
        if not text:
            return ""
        text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
        replacements = {
            "أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي",
            "ة": "ه", "ؤ": "و", "ئ": "ي"
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        text = re.sub(r"[^\w\sء-ي]", "", text)
        return text.strip().lower()
    
    THEMES = {
        "light": {
            "primary": "#2C3E50", "secondary": "#4A5A6A", "success": "#16A34A",
            "warning": "#CA8A04", "danger": "#DC2626", "info": "#2563EB",
            "bg": "#F5F6F7", "card": "#FFFFFF", "text": "#2C3E50",
            "text_secondary": "#64748B", "border": "#E2E8F0", "hover": "#F8FAFC",
            "gradient_start": "#3B82F6", "gradient_end": "#8B5CF6"
        },
        "dark": {
            "primary": "#60A5FA", "secondary": "#94A3B8", "success": "#4ADE80",
            "warning": "#FBBF24", "danger": "#F87171", "info": "#60A5FA",
            "bg": "#0F172A", "card": "#1E293B", "text": "#F1F5F9",
            "text_secondary": "#94A3B8", "border": "#334155", "hover": "#334155",
            "gradient_start": "#3B82F6", "gradient_end": "#8B5CF6"
        }
    }
