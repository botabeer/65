# chain_words_game.py
import random
from games.base_game import BaseGame


class ChainGame(BaseGame):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "سلسلة"

        self.supports_hint = False
        self.supports_reveal = False

        self.starting_words = ["سيارة", "تفاح", "قلم", "نجم", "كتاب", "باب", "رمل"]
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
        return self.build_question_message(
            f"الكلمة السابقة: {self.last_word}",
            f"ابدا بحرف: {required_letter}",
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)

        if normalized in self.used_words:
            return None

        required_letter = self.normalize_text(self.last_word[-1])

        if normalized and normalized[0] == required_letter and len(normalized) >= 2:
            self.used_words.add(normalized)
            points = self.add_score(user_id, display_name, 1)

            self.last_word = user_answer.strip()
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result

            return {"response": self.get_question(), "points": points}

        return None
