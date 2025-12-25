# scramble_word_game.py
import random
from games.base_game import BaseGame


class ScrambleGame(BaseGame):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "ترتيب"

        self.words = [
            "مدرسة", "كتاب", "قلم", "باب",
            "نافذة", "طاولة", "كرسي", "سيارة", "طائرة"
        ]

        random.shuffle(self.words)
        self.used_words = []
        self.current_scrambled = None

    def scramble_word(self, word):
        letters = list(word)
        random.shuffle(letters)
        return " ".join(letters)

    def get_question(self):
        available = [w for w in self.words if w not in self.used_words]
        if not available:
            self.used_words.clear()
            available = self.words.copy()

        word = random.choice(available)
        self.used_words.append(word)

        self.current_answer = word
        self.current_scrambled = self.scramble_word(word)

        return self.build_question_message(
            f"رتب الحروف:\n{self.current_scrambled}"
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)

        if self.supports_hint and normalized == "لمح":
            return {
                "response": self.build_text_message(f"يبدا ب: {self.current_answer[0]}"),
                "points": 0,
            }

        if self.supports_reveal and normalized == "جاوب":
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"الاجابة: {self.current_answer}\n\n{result.get('message', '')}"
                return result

            return {"response": self.get_question(), "points": 0}

        if normalized == self.normalize_text(self.current_answer):
            points = self.add_score(user_id, display_name, 1)
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result

            return {"response": self.get_question(), "points": points}

        return None
