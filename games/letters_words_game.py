import random
from games.base_game import BaseGame

class LettersGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "تكوين"

        # كل الأحرف العربية الممكنة للاختيار العشوائي
        self.arabic_letters = list("ابتثجحخدذرزسشصضطظعغفقكلمنهويء")
        self.current_set = None
        self.found_words = set()
        self.required_words = 3
        self.current_question = 0

    def generate_random_set(self, size=6):
        """توليد مجموعة أحرف عشوائية"""
        return random.sample(self.arabic_letters, size)

    def get_question(self):
        # توليد مجموعة جديدة لكل سؤال
        self.current_set = self.generate_random_set()
        self.found_words.clear()
        letters_display = " ".join(self.current_set)
        return self.build_question_message(
            f"كون كلمات من:\n{letters_display}",
            f"مطلوب {self.required_words} كلمات",
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active:
            return None

        normalized = self.normalize_text(user_answer)

        if normalized in ["ايقاف", "ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)

        # التحقق أن كل أحرف الكلمة موجودة في المجموعة الحالية
        if all(c in self.current_set for c in normalized):
            if normalized not in self.found_words:
                self.found_words.add(normalized)
                points = 1
                self.scores.setdefault(user_id, {"name": display_name, "score": 0})
                self.scores[user_id]["score"] += points

                # إذا اكتملت الكلمات المطلوبة للانتقال للسؤال التالي
                if len(self.found_words) >= self.required_words:
                    self.current_question += 1
                    self.answered_users.clear()
                    self.found_words.clear()
                    return {"response": self.get_question(), "points": points, "next_question": True}

                remaining = self.required_words - len(self.found_words)
                return {
                    "response": self.build_text_message(f"صحيح تبقى {remaining}"),
                    "points": points,
                }

        return {
            "response": self.build_text_message("الكلمة غير صحيحة أو مستخدمة مسبقًا"),
            "points": 0,
        }
