import random
from games.base_game import BaseGame

class ChainGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "سلسله"
        self.supports_hint = True
        self.supports_reveal = True

        self.starting_words = [
            "سيارة", "تفاح", "قلم", "نجم", "كتاب", "باب", "رمل",
            "طائرة", "حديقة", "مدرسة", "كرسي", "شمس", "قمر", "بحر",
            "جبل", "وردة", "شجرة", "كوب", "ساعة", "مفتاح", "باب",
            "نافذة", "طاولة", "مكتب", "قلم", "دفتر", "كتاب", "حقيبة"
        ]

        self.last_word = None
        self.used_words = set()

    def start_game(self):
        self.current_question = 0
        self.game_active = True
        self.last_word = random.choice(self.starting_words)
        self.used_words = {self.normalize_text(self.last_word)}
        self.answered_users.clear()
        return self.get_question()

    def get_question(self):
        required_letter = self.last_word[-1]
        self.previous_question = f"الكلمة السابقة: {self.last_word}"
        self.current_answer = [f"كلمة تبدأ بحرف {required_letter}"]
        
        return self.build_question_message(
            f"الكلمة السابقة: {self.last_word}",
            f"ابدأ بحرف: {required_letter}"
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)

        if normalized in ["ايقاف", "ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)

        if self.supports_hint and normalized == "لمح":
            required_letter = self.normalize_text(self.last_word[-1])
            hint = f"ابدأ بحرف: {required_letter}\nاي كلمة مناسبة"
            return {"response": self.build_text_message(hint), "points": 0}

        if self.supports_reveal and normalized == "جاوب":
            required_letter = self.last_word[-1]
            possible = [w for w in self.starting_words if w.startswith(required_letter) and self.normalize_text(w) not in self.used_words]
            if possible:
                example = random.choice(possible)
            else:
                example = f"كلمة تبدأ بـ {required_letter}"
            
            self.previous_answer = example
            self.last_word = example if possible else self.last_word
            if possible:
                self.used_words.add(self.normalize_text(example))
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                return self.end_game()
            
            return {
                "response": self.get_question(),
                "points": 0
            }

        if normalized in self.used_words:
            return None

        required_letter = self.normalize_text(self.last_word[-1])

        if normalized and normalized[0] == required_letter and len(normalized) >= 2:
            self.used_words.add(normalized)
            self.answered_users.add(user_id)

            points = self.add_score(user_id, display_name, 1)

            self.last_word = user_answer.strip()
            self.previous_answer = user_answer.strip()
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result

            return {
                "response": self.get_question(),
                "points": points
            }

        return None
