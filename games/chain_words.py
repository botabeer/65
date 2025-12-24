import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_loader import BaseGame
from config import normalize_arabic


class ChainWordsGame(BaseGame):
    def __init__(self):
        super().__init__()
        self.name = "لعبة سلسلة الكلمات"
        self.description = "ربط الكلمات - آخر حرف يبدأ به الكلمة التالية"
        self.min_players = 2
        self.max_players = 20
        self.used_words = set()

    def start(self, group_id: str, players: dict) -> tuple[bool, str]:
        from database import db

        start_words = ["كتاب", "مدرسة", "سيارة", "بيت", "قلم"]
        first_word = random.choice(start_words)

        self.used_words = {normalize_arabic(first_word)}

        db.update_game_state(group_id, "last_word", first_word)
        db.update_game_state(group_id, "used_words", list(self.used_words))
        db.update_game_state(group_id, "turn_count", 0)
        db.update_game_state(group_id, "max_turns", 20)

        return True, (
            "لعبة سلسلة الكلمات بدأت\n\n"
            f"الكلمة الأولى: {first_word}\n"
            f"ابدأ بكلمة تبدأ بحرف: {first_word[-1]}"
        )

    def process_message(self, group_id: str, user_id: str, message: str) -> tuple[str | None, bool]:
        from database import db

        word = message.strip()
        if len(word) < 2:
            return None, False

        normalized_word = normalize_arabic(word)
        last_word = db.get_game_state(group_id, "last_word", "")
        used_words = set(db.get_game_state(group_id, "used_words", []))
        turn_count = db.get_game_state(group_id, "turn_count", 0)
        max_turns = db.get_game_state(group_id, "max_turns", 20)

        if normalized_word in used_words:
            return "هذه الكلمة مستخدمة من قبل", True

        if normalize_arabic(word[0]) != normalize_arabic(last_word[-1]):
            return f"يجب أن تبدأ الكلمة بحرف: {last_word[-1]}", True

        player = db.get_player(group_id, user_id)
        if not player:
            return None, False

        db.update_player_score(group_id, user_id, 1)

        used_words.add(normalized_word)
        db.update_game_state(group_id, "last_word", word)
        db.update_game_state(group_id, "used_words", list(used_words))
        db.update_game_state(group_id, "turn_count", turn_count + 1)

        if turn_count + 1 >= max_turns:
            return self._end_game(group_id), True

        return (
            f"صحيح {player.display_name}\n\n"
            f"الكلمة التالية يجب أن تبدأ بـ: {word[-1]}",
            True,
        )

    def _end_game(self, group_id: str) -> str:
        from database import db

        leaderboard = db.get_leaderboard(group_id)
        result = "انتهت اللعبة\n\nالنتائج:\n"

        for i, player in enumerate(leaderboard, 1):
            result += f"{i}. {player.display_name}: {player.score} كلمة\n"

        return result

    def end(self, group_id: str) -> tuple[bool, str]:
        return True, self._end_game(group_id)

    def get_status(self, group_id: str) -> str:
        from database import db

        leaderboard = db.get_leaderboard(group_id)
        turn_count = db.get_game_state(group_id, "turn_count", 0)
        max_turns = db.get_game_state(group_id, "max_turns", 20)

        result = f"الدور {turn_count}/{max_turns}\n\nالنقاط:\n"
        for i, player in enumerate(leaderboard, 1):
            result += f"{i}. {player.display_name}: {player.score}\n"

        return result
