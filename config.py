import os
import re
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "Bot 65"
BOT_VERSION = "2.0"
BOT_CREATOR = "تم إنشاء هذا البوت بواسطة عبير الدوسري @ 2025"

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OWNER_USER_ID = os.getenv("OWNER_USER_ID", "")

SYSTEM_SETTINGS = {
    "port": int(os.getenv("PORT", 10000)),
    "workers": int(os.getenv("WORKERS", 4)),
    "questions_per_game": 5,
    "max_name_length": 50,
    "min_name_length": 1,
    "enable_spam_protection": True,
    "max_messages_per_minute": 15,
    "ban_duration_hours": 1,
    "auto_ban_after_warnings": 3,
}

MESSAGES = {
    "welcome": f"مرحبا بك في {BOT_NAME}",
    "registration_success": "تم تسجيلك بنجاح",
    "game_started": "بدأت اللعبة",
    "game_ended": "انتهت اللعبة",
    "correct_answer": "إجابة صحيحة",
    "wrong_answer": "إجابة خاطئة",
    "game_not_found": "اللعبة غير موجودة",
    "no_active_game": "لا توجد لعبة نشطة",
    "already_registered": "أنت مسجل بالفعل",
    "not_registered": "يجب التسجيل أولا",
    "player_withdrawn": "تم انسحابك من اللعبة",
    "need_min_players": "عدد اللاعبين غير كاف",
    "spam_warning": "تم اكتشاف سبام",
    "user_banned": "تم حظرك مؤقتا",
    "group_only": "هذا الأمر للمجموعات فقط",
    "private_only": "هذا الأمر للمحادثات الخاصة فقط",
}

def normalize_arabic(text):
    if not text:
        return ""
    
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
    
    replacements = {
        "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
        "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    text = re.sub(r"[^\w\sء-ي0-9]", "", text)
    
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

COMMANDS = {
    "private_games": {
        "ذكاء": "IQGame",
        "خمن": "GuessGame",
        "ترتيب": "ScrambleGame",
        "ضد": "OppositeGame",
        "كتابه": "FastTypingGame",
        "انسان": "HumanAnimalGame",
        "كلمات": "LettersWordsGame",
        "اغنيه": "SongGame",
        "توافق": "CompatibilityGame",
    },
    "group_games": {
        "سلسله": "ChainWordsGame",
        "الوان": "WordColorGame",
        "مافيا": "MafiaGame",
    },
    "text_commands": {
        "تحدي": "challenges.txt",
        "اعتراف": "confessions.txt",
        "منشن": "mentions.txt",
        "شخصيه": "personality.txt",
        "سؤال": "questions.txt",
        "حكمه": "quotes.txt",
        "موقف": "situations.txt",
    },
    "game_controls": {
        "لمح": "hint",
        "جاوب": "reveal",
        "ايقاف": "stop",
        "انسحب": "withdraw",
    },
    "group_controls": {
        "تسجيل": "register",
        "حاله": "status",
        "صداره": "leaderboard",
        "انهاء": "end_game",
    },
    "general": {
        "ابدا": "start",
        "مساعده": "help",
        "ثيم": "theme",
        "معلومات": "info",
    }
}
