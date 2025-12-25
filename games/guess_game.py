# guess_game.py
import random
from games.base_game import BaseGame


class GuessGame(BaseGame):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "خمن"

        self.items = {
            "المطبخ": {"ق": ["قدر"], "م": ["ملعقة"], "س": ["سكين"]},
            "غرفة النوم": {"س": ["سرير"], "و": ["وسادة"], "م": ["مراة"]},
            "المدرسة": {"ق": ["قلم"], "د": ["دفتر"], "ك": ["كتاب"]},
            "الفواكه": {"ت": ["تفاح"], "م": ["موز"], "ع": ["عنب"]},
            "الحيوانات": {"ق": ["قطة"], "ف": ["فيل"], "ا": ["اسد"]},
        }

        self.questions_list = []
        for category, letters in self.items.items():
            for letter, words in letters.items():
                self.questions_list.append({
                    "category": category,
                    "letter": letter,
                    "answers": words
                })

        random.shuffle(self.questions_list)

    def get_question(self):
        q = self.questions_list[self.current_question % len(self.questions_list)]
        self.current_answer = q["answers"]
        return self.build_question_message(
            f"الفئة: {q['category']}\nيبدا بحرف: {q['letter']}"
        )

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
