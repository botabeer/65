# letters_words_game.py
import random
from games.base_game import BaseGame


class LettersGame(BaseGame):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "تكوين"

        self.letter_sets = [
            {"letters": ["ق", "ل", "م", "ع", "ر"], "words": ["قلم", "علم", "عمر"]},
            {"letters": ["ك", "ت", "ا", "ب", "م"], "words": ["كتاب", "كتب", "مكتب"]},
            {"letters": ["د", "ر", "س", "ة", "م"], "words": ["مدرسة", "درس", "مدرس"]},
        ]

        random.shuffle(self.letter_sets)

        self.current_set = None
        self.found_words = set()
        self.required_words = 2

    def get_question(self):
        q = self.letter_sets[self.current_question % len(self.letter_sets)]
        self.current_set = q
        self.current_answer = q["words"]

        self.found_words.clear()

        letters_display = " ".join(q["letters"])
        return self.build_question_message(
            f"كون كلمات من:\n{letters_display}",
            f"مطلوب {self.required_words} كلمات",
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active:
            return None

        normalized = self.normalize_text(user_answer)

        if self.supports_hint and normalized == "لمح":
            remaining = [
                w for w in self.current_answer
                if self.normalize_text(w) not in self.found_words
            ]
            if remaining:
                return {
                    "response": self.build_text_message(f"يبدا ب: {remaining[0][0]}"),
                    "points": 0,
                }

        if self.supports_reveal and normalized == "جاوب":
            words = " - ".join(self.current_answer)
            self.current_question += 1
            self.answered_users.clear()
            self.found_words.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"كلمات ممكنة: {words}\n\n{result.get('message', '')}"
                return result

            return {"response": self.get_question(), "points": 0}

        valid_words = [self.normalize_text(w) for w in self.current_answer]

        if normalized not in valid_words or normalized in self.found_words:
            return None

        self.found_words.add(normalized)

        points = 1
        self.scores.setdefault(user_id, {"name": display_name, "score": 0})
        self.scores[user_id]["score"] += points

        if len(self.found_words) >= self.required_words:
            self.current_question += 1
            self.answered_users.clear()
            self.found_words.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result

            return {"response": self.get_question(), "points": points}

        remaining = self.required_words - len(self.found_words)
        return {
            "response": self.build_text_message(f"صحيح تبقى {remaining}"),
            "points": points,
        }
