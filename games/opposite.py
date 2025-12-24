import random
from games.base import BaseGame
from config import normalize_arabic


class OppositeGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة الأضداد"
        self.opposites = [
            {"word": "كبير", "opposite": ["صغير", "قصير"]},
            {"word": "طويل", "opposite": ["قصير"]},
            {"word": "سريع", "opposite": ["بطيء", "بطي"]},
            {"word": "ساخن", "opposite": ["بارد"]},
            {"word": "نظيف", "opposite": ["وسخ", "قذر"]},
            {"word": "جميل", "opposite": ["قبيح"]},
            {"word": "غني", "opposite": ["فقير"]},
            {"word": "قوي", "opposite": ["ضعيف"]},
        ]
        random.shuffle(self.opposites)

    def get_question(self):
        pair = self.opposites[self.current_q - 1]
        self.current_answer = pair["opposite"]

        question = f"ما هو عكس كلمة:\n{pair['word']}"
        hint = f"الإجابات المحتملة: {len(pair['opposite'])}"
        return self.build_question_flex(question, hint)

    def check_answer(self, answer: str) -> bool:
        normalized = normalize_arabic(answer)
        return any(normalized == normalize_arabic(ans) for ans in self.current_answer)
