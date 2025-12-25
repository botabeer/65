# iq_game.py
import random
from games.base_game import BaseGame


class IqGame(BaseGame):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "ذكاء"

        self.riddles = [
            {"q": "ما الشيء الذي يمشي بلا ارجل ويبكي بلا عيون", "a": ["السحاب", "الغيم"]},
            {"q": "له راس ولكن لا عين له", "a": ["الدبوس", "المسمار"]},
            {"q": "شيء كلما زاد نقص", "a": ["العمر"]},
            {"q": "يكتب ولا يقرا ابدا", "a": ["القلم"]},
            {"q": "له اسنان كثيرة ولكنه لا يعض", "a": ["المشط"]},
            {"q": "يوجد في الماء ولكن الماء يميته", "a": ["الملح"]},
            {"q": "يتكلم بجميع اللغات دون ان يتعلمها", "a": ["الصدى"]},
            {"q": "شيء كلما اخذت منه كبر", "a": ["الحفرة"]},
            {"q": "يخترق الزجاج ولا يكسره", "a": ["الضوء"]},
            {"q": "يسمع بلا اذن ويتكلم بلا لسان", "a": ["الهاتف"]},
        ]

        random.shuffle(self.riddles)
        self.used_riddles = []

    def get_question(self):
        available = [r for r in self.riddles if r not in self.used_riddles]
        if not available:
            self.used_riddles.clear()
            available = self.riddles.copy()

        riddle = random.choice(available)
        self.used_riddles.append(riddle)
        self.current_answer = riddle["a"]
        return self.build_question_message(riddle["q"])

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
            answers = " او ".join(self.current_answer)
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"الاجابة: {answers}\n\n{result.get('message', '')}"
                return result

            return {
                "message": f"الاجابة: {answers}",
                "response": self.get_question(),
                "points": 0,
            }

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
