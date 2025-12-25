# category_letter_game.py
import random
from games.base_game import BaseGame


class CategoryGame(BaseGame):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "فئة"

        self.challenges = [
            {"category": "المطبخ", "letter": "ق", "answers": ["قدر", "قلاية"]},
            {"category": "حيوان", "letter": "ب", "answers": ["بطة", "بقرة"]},
            {"category": "فاكهة", "letter": "ت", "answers": ["تفاح", "توت"]},
            {"category": "بلاد", "letter": "س", "answers": ["سعودية", "سوريا"]},
            {"category": "اسم ولد", "letter": "م", "answers": ["محمد", "مصطفى"]},
        ]

        self.questions = []
        self.first_correct_answer = False

    def start_game(self):
        self.questions = random.sample(
            self.challenges,
            min(self.questions_count, len(self.challenges))
        )
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        self.first_correct_answer = False
        self.game_active = True
        return self.get_question()

    def get_question(self):
        challenge = self.questions[self.current_question]
        self.first_correct_answer = False
        return self.build_question_message(
            f"الفئة: {challenge['category']}\nالحرف: {challenge['letter']}"
        )

    def check_answer(self, user_answer, user_id, display_name):
        if self.first_correct_answer or user_id in self.answered_users:
            return None

        challenge = self.questions[self.current_question]
        normalized = self.normalize_text(user_answer)

        if self.supports_hint and normalized == "لمح":
            sample = challenge["answers"][0]
            return {
                "response": self.build_text_message(f"يبدا بحرف: {sample[0]}"),
                "points": 0,
            }

        if self.supports_reveal and normalized == "جاوب":
            answers = " - ".join(challenge["answers"])
            self.first_correct_answer = True
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                return self._end_game()

            return {
                "response": self.build_text_message(f"بعض الاجابات:\n{answers}"),
                "points": 0,
            }

        valid = [self.normalize_text(a) for a in challenge["answers"]]
        if normalized in valid:
            points = self.add_score(user_id, display_name, 1)
            self.first_correct_answer = True
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                return self._end_game()

            return {
                "response": self.build_text_message(f"اجابة صحيحة {display_name}"),
                "points": points,
            }

        return None

    def _end_game(self):
        if not self.scores:
            return {
                "response": self.build_text_message("انتهت اللعبة"),
                "points": 0,
                "game_over": True,
            }

        winner = max(self.scores.values(), key=lambda x: x["score"])
        text = f"انتهت اللعبة\n\nالفائز: {winner['name']}\nالنقاط: {winner['score']}"
        return {
            "response": self.build_text_message(text),
            "points": winner["score"],
            "game_over": True,
        }
