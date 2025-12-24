import random
from games.base import BaseGame
from config import normalize_arabic


class SongGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة الأغاني"
        self.songs = [
            {
                "lyric": "رجعت لي أيام الماضي معاك",
                "artist": ["ام كلثوم", "أم كلثوم"],
            },
            {
                "lyric": "الأطلال باقي الأطلال",
                "artist": ["ام كلثوم", "أم كلثوم"],
            },
            {
                "lyric": "قارئة الفنجان",
                "artist": ["عبدالحليم حافظ", "عبد الحليم حافظ"],
            },
            {
                "lyric": "على قد الشوق",
                "artist": ["عبدالحليم حافظ", "عبد الحليم حافظ"],
            },
        ]
        random.shuffle(self.songs)

    def get_question(self):
        song = self.songs[self.current_q - 1]
        self.current_answer = song["artist"]

        question = f"من يغني:\n{song['lyric']}"
        hint = f"عدد الإجابات: {len(song['artist'])}"
        return self.build_question_flex(question, hint)

    def check_answer(self, answer: str) -> bool:
        normalized = normalize_arabic(answer)
        return any(normalized == normalize_arabic(a) for a in self.current_answer)
