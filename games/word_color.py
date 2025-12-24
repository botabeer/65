import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_loader import BaseGame
from config import normalize_arabic


class WordColorGame(BaseGame):
    def __init__(self):
        super().__init__()
        self.name = "لعبة الألوان"
        self.description = "خمن لون الكلمة وليس معناها"
        self.min_players = 2
        self.max_players = 20
        self.colors = {
            "احمر": "أحمر",
            "أحمر": "أحمر",
            "ازرق": "أزرق",
            "أزرق": "أزرق",
            "اخضر": "أخضر",
            "أخضر": "أخضر",
            "اصفر": "أصفر",
            "أصفر": "أصفر",
        }

    def start(self, group_id: str, players: dict) -> tuple[bool, str]:
        from database import db

        db.update_game_state(group_id, "question_count", 0)
        db.update_game_state(group_id, "max_questions", 10)

        return True, self._next_question(group_id)

    def _next_question(self, group_id: str) -> str:
        from database import db

        word = random.choice(list(self.colors.keys()))
        actual_color = random.choice(list(self.colors.keys()))

        if random.random() < 0.7:
            while actual_color == word:
                actual_color = random.choice(list(self.colors.keys()))

        db.update_game_state(
            group_id,
            "current_answer",
            [actual_color, self.colors[actual_color]],
        )

        question_count = db.get_game_state(group_id, "question_count", 0) + 1
        db.update_game_state(group_id, "question_count", question_count)

        return (
            f"السؤال {question_count}\n\n"
            "ما لون هذه الكلمة؟\n"
            f"{self.colors[word]}\n\n"
            "(اللون الفعلي للكلمة، ليس معناها)"
        )

    def process_message(self, group_id: str, user_id: str, message: str) -> tuple[str | None, bool]:
        from database import db

        current_answer = db.get_game_state(group_id, "current_answer", [])
        if not current_answer:
            return None, False

        normalized = normalize_arabic(message)
        is_correct = any(
            normalized == normalize_arabic(ans) for ans in current_answer
        )

        player = db.get_player(group_id, user_id)
        if not player:
            return None, False

        if is_correct:
            db.update_player_score(group_id, user_id, 1)

            question_count = db.get_game_state(group_id, "question_count", 0)
            max_questions = db.get_game_state(group_id, "max_questions", 10)

            if question_count >= max_questions:
                return self._end_game(group_id), True

            return f"صحيح {player.display_name}\n\n{self._next_question(group_id)}", True

        return f"خطأ {player.display_name}", True

    def _end_game(self, group_id: str) -> str:
        from database import db

        leaderboard = db.get_leaderboard(group_id)
        result = "انتهت لعبة الألوان\n\nالنتائج:\n"

        for i, player in enumerate(leaderboard, 1):
            result += f"{i}. {player.display_name}: {player.score}\n"

        return result

    def end(self, group_id: str) -> tuple[bool, str]:
        return True, self._end_game(group_id)
