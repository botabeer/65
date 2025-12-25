import random
from games.base_game import BaseGame

class LettersGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "تكوين"

        self.letter_sets = [
            {"letters": ["ق", "ل", "م", "ع", "ر"], "words": ["قلم", "علم", "عمر"]},
            {"letters": ["ك", "ت", "ا", "ب", "م"], "words": ["كتاب", "كتب", "مكتب"]},
            {"letters": ["د", "ر", "س", "ة", "م"], "words": ["مدرسة", "درس", "مدرس"]},
            {"letters": ["ح", "د", "ي", "ق", "ة"], "words": ["حديقة", "حدق", "دقيق"]},
            {"letters": ["ط", "ا", "و", "ل", "ة"], "words": ["طاولة", "طول", "والة"]},
            {"letters": ["س", "ي", "ا", "ر", "ة"], "words": ["سيارة", "سار", "راس"]},
            {"letters": ["ش", "ج", "ر", "ة", "ت"], "words": ["شجرة", "شجر", "جرت"]},
            {"letters": ["ن", "ا", "ف", "ذ", "ة"], "words": ["نافذة", "نفذ", "اذن"]},
            {"letters": ["م", "ك", "ت", "ب", "ة"], "words": ["مكتبة", "مكتب", "كتب"]},
            {"letters": ["ح", "ق", "ي", "ب", "ة"], "words": ["حقيبة", "حبيب", "حقب"]},
            {"letters": ["ط", "ا", "ئ", "ر", "ة"], "words": ["طائرة", "طار", "رائ"]},
            {"letters": ["س", "ر", "ي", "ر", "ة"], "words": ["سرير", "سير", "رير"]},
            {"letters": ["و", "س", "ا", "د", "ة"], "words": ["وسادة", "وساد", "سادة"]},
            {"letters": ["م", "ر", "ا", "ة", "ت"], "words": ["مراة", "مرات", "رمت"]},
            {"letters": ["خ", "ز", "ا", "ن", "ة"], "words": ["خزانة", "خزان", "زان"]},
            {"letters": ["م", "ل", "ع", "ق", "ة"], "words": ["ملعقة", "معلق", "علق"]},
            {"letters": ["ص", "ح", "ن", "و", "ة"], "words": ["صحن", "حصن", "نحو"]},
            {"letters": ["ف", "ن", "ج", "ا", "ن"], "words": ["فنجان", "فنان", "جان"]},
            {"letters": ["ق", "د", "ر", "ة", "ت"], "words": ["قدر", "درة", "قدرة"]},
            {"letters": ["س", "ك", "ي", "ن", "ة"], "words": ["سكين", "سكن", "نسك"]},
            {"letters": ["ف", "ر", "ن", "ة", "ت"], "words": ["فرن", "فرة", "نفر"]},
            {"letters": ["ث", "ل", "ا", "ج", "ة"], "words": ["ثلاجة", "ثلج", "لجا"]},
            {"letters": ["م", "ك", "ن", "س", "ة"], "words": ["مكنسة", "مسكن", "سكن"]},
            {"letters": ["م", "م", "س", "ح", "ة"], "words": ["ممسحة", "مسح", "محس"]},
            {"letters": ["ص", "ا", "ب", "و", "ن"], "words": ["صابون", "صاب", "بون"]},
            {"letters": ["م", "ن", "ش", "ف", "ة"], "words": ["منشفة", "منش", "شفن"]},
            {"letters": ["ف", "ر", "ش", "ا", "ة"], "words": ["فرشاة", "فرش", "رشا"]},
            {"letters": ["م", "ع", "ج", "و", "ن"], "words": ["معجون", "معج", "جون"]},
            {"letters": ["ش", "ا", "م", "ب", "و"], "words": ["شامبو", "شام", "بوش"]},
            {"letters": ["ص", "ن", "د", "ل", "ة"], "words": ["صندل", "صدل", "ندل"]}
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

        if normalized in ["ايقاف", "ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)

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
                result["message"] = f"كلمات ممكنة: {words}"
                return result

            return {"response": self.get_question(), "points": 0, "next_question": True}

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

            return {"response": self.get_question(), "points": points, "next_question": True}

        remaining = self.required_words - len(self.found_words)
        return {
            "response": self.build_text_message(f"صحيح تبقى {remaining}"),
            "points": points,
        }
