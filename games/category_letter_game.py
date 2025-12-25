import random
from games.base_game import BaseGame

class CategoryGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(
            line_bot_api,
            game_type="competitive",
            difficulty=difficulty,
            theme=theme
        )

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
        self.previous_question = f"{challenge['category']} حرف {challenge['letter']}"

        return self.build_question_message(
            f"الفئة: {challenge['category']}\nالحرف: {challenge['letter']}"
        )

    def check_answer(self, user_answer, user_id, display_name):
        if self.first_correct_answer or user_id in self.answered_users:
            return None

        challenge = self.questions[self.current_question]
        normalized = self.normalize_text(user_answer)

        if normalized in ["انسحب", "انسحاب"]:
            return self.handle_withdrawal(user_id, display_name)

        if self.supports_hint and normalized == "لمح":
            sample = challenge["answers"][0]
            return {
                "response": self.build_text_message(f"يبدا بحرف: {sample[0]}"),
                "points": 0,
            }

        if self.supports_reveal and normalized == "جاوب":
            answers = " - ".join(challenge["answers"])
            self.first_correct_answer = True
            self.previous_answer = answers
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                return self.end_game()

            return {
                "response": self.get_question(),
                "points": 0,
                "next_question": True
            }

        valid_answers = [self.normalize_text(a) for a in challenge["answers"]]

        if normalized in valid_answers:
            self.answered_users.add(user_id)
            points = self.add_score(user_id, display_name, 1)

            self.first_correct_answer = True
            self.previous_answer = user_answer.strip()
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result

            return {
                "response": self.get_question(),
                "points": points,
                "next_question": True
            }

        return None
