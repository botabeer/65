import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_loader import BaseGame


class MafiaGame(BaseGame):
    def __init__(self):
        super().__init__()
        self.name = "لعبة المافيا"
        self.description = "لعبة اجتماعية - مافيا ضد مواطنين"
        self.min_players = 4
        self.max_players = 15

    def start(self, group_id: str, players: dict) -> tuple[bool, str]:
        from database import db

        player_count = len(players)
        num_mafia = max(1, player_count // 4)

        roles_list = ["مافيا"] * num_mafia
        roles_list += ["مواطن"] * (player_count - num_mafia)

        random.shuffle(roles_list)

        player_ids = list(players.keys())
        random.shuffle(player_ids)

        roles = dict(zip(player_ids, roles_list))

        db.update_game_state(group_id, "roles", roles)
        db.update_game_state(group_id, "alive", player_ids.copy())
        db.update_game_state(group_id, "phase", "night")
        db.update_game_state(group_id, "day_count", 1)

        return True, (
            "بدأت لعبة المافيا\n\n"
            f"عدد اللاعبين: {player_count}\n"
            f"المافيا: {num_mafia}\n"
            f"المواطنون: {player_count - num_mafia}\n\n"
            "الليل الأول\n"
            "المافيا: اختاروا ضحيتكم"
        )

    def process_message(self, group_id: str, user_id: str, message: str) -> tuple[str | None, bool]:
        return None, False

    def end(self, group_id: str) -> tuple[bool, str]:
        from database import db

        roles = db.get_game_state(group_id, "roles", {})
        players = db.get_session(group_id).players

        result = "تم إيقاف اللعبة\n\nالأدوار:\n"
        for user_id, role in roles.items():
            result += f"{players[user_id].display_name}: {role}\n"

        return True, result
