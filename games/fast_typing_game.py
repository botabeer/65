# fast_typing_game.py
import random
import time
from smart_base_game import SmartBaseGame

class FastGame(SmartBaseGame):
    def __init__(self, line_bot_api=None, questions_count=5):
        super().__init__(line_bot_api, questions_count=questions_count, game_type="fast")
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

        subtitle = f"الوقت: {self.round_time} ثانية"
        return self.build_question(phrase + "\n" + subtitle)

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        elapsed = time.time() - self.round_start_time
        if elapsed > self.round_time:
            self.current_question += 1
            self.answered_users.clear()
            if self.current_question >= self.questions_count:
                return self.end_game()
            return self.get_question()

        if user_answer.strip() == self.current_answer:
            points = self.add_score(user_id, display_name, 1)
            self.current_question += 1
            self.answered_users.clear()
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result
            return self.get_question()
        return None
