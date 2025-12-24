import random
from games.base import BaseGame
from config import normalize_arabic


class ScrambleGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة ترتيب الحروف"
        self.words = {
            1: ["كتاب", "قلم", "باب", "حقيبه", "مدرسه"],
            2: ["سياره", "مطبخ", "تلفاز", "حاسوب", "تفاحه"],
            3: ["مستشفى", "جامعه", "مكتبه", "هاتف", "صحيفه"],
        }

    def get_question(self):
        level = min(3, (self.current_q + 4) // 5 + 1)
        word = random.choice(self.words[level])
        self.current_answer = word

        scrambled = list(word)
        random.shuffle(scrambled)
        while "".join(scrambled) == word:
            random.shuffle(scrambled)

        question = f"رتب الحروف:\n{' '.join(scrambled)}"
        hint = f"{len(word)} أحرف"
        return self.build_question_flex(question, hint)

    def check_answer(self, answer: str) -> bool:
        return normalize_arabic(answer) == normalize_arabic(self.current_answer)
