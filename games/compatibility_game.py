# compatibility_game.py
from smart_base_game import SmartBaseGame
import re

class CompatibilityGame(SmartBaseGame):
    """لعبة حساب نسبة التوافق"""
    def __init__(self, line_bot_api=None):
        super().__init__(line_bot_api, questions_count=1, game_type="entertainment")
        self.game_name = "توافق"
        self.supports_hint = False
        self.supports_reveal = False

    def is_valid_text(self, text: str) -> bool:
        """التحقق من أن النص أسماء فقط"""
        return not re.search(r"[@#0-9A-Za-z!$%^&*()_+=\[\]{};:'\"\\|,.<>/?~`]", text)

    def parse_names(self, text: str) -> tuple:
        text = ' '.join(text.split())
        if ' و ' in text:
            parts = text.split(' و ', 1)
            return (parts[0].strip(), parts[1].strip())
        words = text.split()
        if 'و' in words:
            idx = words.index('و')
            return (' '.join(words[:idx]).strip(), ' '.join(words[idx+1:]).strip())
        return (None, None)

    def calculate_compatibility(self, name1: str, name2: str) -> int:
        n1 = self.normalize_text(name1)
        n2 = self.normalize_text(name2)
        combined = ''.join(sorted([n1, n2]))
        seed = sum(ord(c)*(i+1) for i,c in enumerate(combined))
        return (seed % 81) + 20  # نسبة 20-100

    def get_compatibility_message(self, percentage: int) -> str:
        if percentage >= 90: return "توافق عالي جدا"
        if percentage >= 75: return "توافق عالي"
        if percentage >= 60: return "توافق جيد"
        if percentage >= 45: return "توافق متوسط"
        return "توافق منخفض"

    def start_game(self):
        self.game_active = True
        return self.get_question()

    def get_question(self):
        return self.build_question("أدخل اسمين بينهما (و)\nمثال: اسم و اسم")

    def check_answer(self, user_answer, user_id=None, display_name=None):
        if not self.game_active:
            return None

        name1, name2 = self.parse_names(user_answer)
        if not name1 or not name2:
            return {"response": self.build_question("الصيغة غير صحيحة\nاكتب: اسم و اسم\nمثال: اسم و اسم"), "points":0}

        if not self.is_valid_text(name1) or not self.is_valid_text(name2):
            return {"response": self.build_question("غير مسموح بالرموز أو الأرقام\nاكتب اسمين نصيين فقط"), "points":0}

        percentage = self.calculate_compatibility(name1, name2)
        message_text = self.get_compatibility_message(percentage)

        result_text = f"نتيجة التوافق\n\n{name1} و {name2}\n\nالنسبة: {percentage}%\n{message_text}\n\nملاحظة: نفس النتيجة لو كتبت {name2} و {name1}"

        self.game_active = False
        return {
            "response": self.build_question(result_text),
            "points":0,
            "game_over": True
        }
