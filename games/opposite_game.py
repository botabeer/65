# opposite_game.py
import random
from games.base_game import BaseGame


class OppositeGame(BaseGame):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "ضد"

        self.opposites = {
            "كبير": ["صغير"],
            "طويل": ["قصير"],
            "سريع": ["بطيء"],
            "ساخن": ["بارد"],
            "نظيف": ["وسخ"],
            "جديد": ["قديم"],
            "صعب": ["سهل"],
            "قوي": ["ضعيف"],
            "غني": ["فقير"],
            "سعيد": ["حزين"],
            "جميل": ["قبيح"],
            "ثقيل": ["خفيف"],
        }

        self.questions_list = list(self.opposites.items())
        random.shuffle(self.questions_list)

    def get_question(self):
        word, answers = self.questions_list[self.current_question % len(self.questions_list)]
        self.current_answer = answers
        return self.build_question_message(f"ما عكس كلمة:\n{word}")

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)

        if self.supports_hint and normalized == "لمح":
            return {
                "response": self.build_text_message(f"يبدا ب: {self.current_answer[0][0]}"),
                "points": 0,
            }

        if self.supports_reveal and normalized == "جاوب":
            self.current_question += 1
            self.answered_users.clear()
            if self.current_question >= self.questions_count:
                return self.end_game()
            return {"response": self.get_question(), "points": 0}

        for correct in self.current_answer:
            if self.normalize_text(correct) == normalized:
                points = self.add_score(user_id, display_name, 1)
                self.current_question += 1
                self.answered_users.clear()
                if self.current_question >= self.questions_count:
                    result = self.end_game()
                    result["points"] = points
                    return result
                return {"response": self.get_question(), "points": points}

        return None
