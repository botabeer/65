# fast_typing_game.py
import random
import time
from games.base_game import BaseGame


class FastGame(BaseGame):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "اسرع"

        self.supports_hint = False
        self.supports_reveal = False

        self.round_time = 20
        self.round_start_time = None

        self.phrases = [
            "سبحان الله",
            "الحمد لله",
            "الله اكبر",
            "لا اله الا الله",
        ]

        random.shuffle(self.phrases)
        self.used_phrases = []

    def get_question(self):
        available = [p for p in self.phrases if p not in self.used_phrases]
        if not available:
            self.used_phrases.clear()
            available = self.phrases.copy()

        phrase = random.choice(available)
        self.used_phrases.append(phrase)

        self.current_answer = phrase
        self.round_start_time = time.time()

        return self.build_question_message(
            phrase,
            f"الوقت: {self.round_time} ثانية",
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        if time.time() - self.round_start_time > self.round_time:
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                return self.end_game()

            return {"response": self.get_question(), "points": 0}

        if user_answer.strip() == self.current_answer:
            points = self.add_score(user_id, display_name, 1)
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result

            return {"response": self.get_question(), "points": points}

        return None
