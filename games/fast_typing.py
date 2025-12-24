import random
import time
from games.base import BaseGame
from config import normalize_arabic


class FastTypingGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة الكتابة السريعة"
        self.supports_hint = False
        self.time_limit = 10
        self.start_time = None
        self.phrases = [
            "سبحان الله",
            "الحمد لله",
            "لا إله إلا الله",
            "الله أكبر",
            "استغفر الله",
        ]

    def get_question(self):
        phrase = random.choice(self.phrases)
        self.current_answer = phrase
        self.start_time = time.time()

        question = (
            f"اكتب العبارة التالية بسرعة:\n{phrase}\n\n"
            f"الوقت: {self.time_limit} ثانية"
        )
        return self.build_question_flex(question, None)

    def check_answer(self, answer: str) -> bool:
        if self.start_time and (time.time() - self.start_time) > self.time_limit:
            return False

        return normalize_arabic(answer) == normalize_arabic(self.current_answer)
