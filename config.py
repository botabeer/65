import os
import re
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
DB_PATH = os.getenv("DB_PATH", "botmesh.db")
PORT = int(os.getenv("PORT", 5000))
WORKERS = int(os.getenv("WORKERS", 4))
ENV = os.getenv("ENV", "production")

BOT_NAME = "Bot 65"
BOT_VERSION = "2.0"
OWNER_USER_ID = "YOUR_LINE_USER_ID_HERE"

SYSTEM_SETTINGS = {
    'port': PORT,
    'enable_spam_protection': True,
    'clean_old_sessions': True,
    'session_cleanup_hours': 24
}

SECURITY_SETTINGS = {
    'enable_spam_protection': True,
    'max_messages_per_minute': 15,
    'ban_duration': timedelta(hours=1),
    'auto_ban_after_warnings': 3
}

MESSAGES = {
    'registration_success': 'تم التسجيل بنجاح',
    'game_not_found': 'اللعبة غير موجودة',
    'no_active_game': 'لا توجد لعبة نشطة',
    'spam_warning': 'تم اكتشاف سبام. الرجاء التوقف مؤقتا',
    'banned': 'تم حظرك مؤقتا بسبب السبام',
    'group_only': 'هذا الأمر للمجموعات فقط',
    'need_game': 'يجب اختيار لعبة اولا',
    'already_active': 'اللعبة نشطة بالفعل',
    'min_players': 'عدد اللاعبين غير كافي'
}

class Config:
    QUESTIONS_PER_GAME = 5
    MAX_NAME_LENGTH = 50
    MIN_NAME_LENGTH = 1
    
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
            "primary": "#2C3E50",
            "secondary": "#4A5A6A",
            "success": "#16A34A",
            "warning": "#CA8A04",
            "danger": "#DC2626",
            "info": "#2563EB",
            "bg": "#F5F6F7",
            "card": "#FFFFFF",
            "text": "#2C3E50",
            "text_secondary": "#64748B",
            "border": "#E2E8F0",
            "hover": "#F8FAFC"
        },
        "dark": {
            "primary": "#60A5FA",
            "secondary": "#94A3B8",
            "success": "#4ADE80",
            "warning": "#FBBF24",
            "danger": "#F87171",
            "info": "#60A5FA",
            "bg": "#0F172A",
            "card": "#1E293B",
            "text": "#F1F5F9",
            "text_secondary": "#94A3B8",
            "border": "#334155",
            "hover": "#334155"
        }
    }
