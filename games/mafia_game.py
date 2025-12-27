from linebot.v3.messaging import FlexMessage, FlexContainer, TextMessage
from games.base_game import BaseGame
import random
from collections import Counter


class MafiaGame(BaseGame):
    def __init__(self, line_bot_api, theme="light"):
        super().__init__(line_bot_api, theme, game_type="social")
        self.game_name = "مافيا"

        self.min_players = 4
        self.max_players = 15

        self.players = {}        # user_id -> name
        self.roles = {}          # user_id -> role
        self.alive = set()

        self.mafia = set()
        self.doctor = None
        self.detective = None

        self.phase = "lobby"     # lobby | night | day | end
        self.night_actions = {}
        self.votes = {}

    # =========================
    # Router اللعبة
    # =========================
    def handle(self, user_id, display_name, text):
        if text == "مافيا":
            return self.lobby()

        if text == "mafia_join":
            return self.join(user_id, display_name)

        if text == "mafia_start":
            return self.start_mafia()

        if text.startswith("mafia_night_"):
            return self.night_action(user_id, text.replace("mafia_night_", ""))

        if text.startswith("mafia_vote_"):
            return self.vote(user_id, text.replace("mafia_vote_", ""))

        if text == "ايقاف":
            return self.end_mafia("تم إيقاف اللعبة")

        return None

    # =========================
    # 🎭 توزيع الأدوار
    # =========================
    def assign_roles(self):
        ids = list(self.players.keys())
        random.shuffle(ids)

        mafia_count = 1 if len(ids) < 7 else 2
        self.mafia = set(ids[:mafia_count])
        self.doctor = ids[mafia_count]
        self.detective = ids[mafia_count + 1]

        for uid in ids:
            if uid in self.mafia:
                self.roles[uid] = "مافيا"
            elif uid == self.doctor:
                self.roles[uid] = "دكتور"
            elif uid == self.detective:
                self.roles[uid] = "محقق"
            else:
                self.roles[uid] = "مواطن"

            self.line_bot_api.push_message(
                uid,
                TextMessage(text=f"دورك: {self.roles[uid]}")
            )

    # =========================
    # 🏠 الواجهة
    # =========================
    def lobby(self):
        c = self.get_theme_colors()
        return FlexMessage(
            alt_text="لعبة المافيا",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box", "layout": "vertical",
                    "paddingAll": "20px", "backgroundColor": c["bg"],
                    "contents": [
                        {"type": "text", "text": "لعبة المافيا",
                         "size": "xl", "weight": "bold",
                         "align": "center", "color": c["primary"]},
                        {"type": "separator", "margin": "md"},
                        {"type": "text",
                         "text": f"اللاعبون: {len(self.players)}/{self.max_players}",
                         "align": "center", "color": c["text"]}
                    ]
                },
                "footer": {
                    "type": "box", "layout": "vertical",
                    "contents": [
                        {"type": "button",
                         "action": {"type": "message", "label": "انضمام", "text": "mafia_join"},
                         "style": "secondary"},
                        {"type": "button",
                         "action": {"type": "message", "label": "بدء", "text": "mafia_start"},
                         "style": "secondary"}
                    ]
                }
            })
        )

    # =========================
    # 🚪 انضمام
    # =========================
    def join(self, user_id, name):
        if user_id not in self.players and len(self.players) < self.max_players:
            self.players[user_id] = name
            self.alive.add(user_id)
        return self.lobby()

    # =========================
    # ▶️ بدء اللعبة
    # =========================
    def start_mafia(self):
        if len(self.players) < self.min_players:
            return TextMessage(text="عدد اللاعبين غير كاف")

        self.assign_roles()
        self.phase = "night"
        return self.player_buttons("مرحلة الليل", "mafia_night_")

    # =========================
    # 🌙 الليل
    # =========================
    def night_action(self, uid, target):
        if uid not in self.alive:
            return None

        role = self.roles.get(uid)
        if role in ("مافيا", "دكتور"):
            self.night_actions[role] = target

        if "مافيا" in self.night_actions and "دكتور" in self.night_actions:
            return self.resolve_night()

        return None

    def resolve_night(self):
        killed = self.night_actions.get("مافيا")
        saved = self.night_actions.get("دكتور")

        if killed and killed != saved and killed in self.alive:
            self.alive.remove(killed)

        self.night_actions = {}
        self.phase = "day"
        return self.player_buttons("مرحلة التصويت", "mafia_vote_")

    # =========================
    # ☀️ النهار
    # =========================
    def vote(self, uid, target):
        if uid in self.alive:
            self.votes[uid] = target

        if len(self.votes) >= len(self.alive):
            return self.resolve_day()

        return None

    def resolve_day(self):
        voted = Counter(self.votes.values()).most_common(1)[0][0]
        if voted in self.alive:
            self.alive.remove(voted)

        self.votes = {}
        return self.check_win()

    # =========================
    # 🏁 الفوز
    # =========================
    def check_win(self):
        mafia_alive = self.mafia & self.alive
        citizens_alive = self.alive - mafia_alive

        if not mafia_alive:
            return self.end_mafia("المواطنون فازوا")

        if len(mafia_alive) >= len(citizens_alive):
            return self.end_mafia("المافيا فازت")

        self.phase = "night"
        return self.player_buttons("مرحلة الليل", "mafia_night_")

    # =========================
    # 🔘 أزرار اللاعبين
    # =========================
    def player_buttons(self, title, prefix):
        c = self.get_theme_colors()
        buttons = [
            {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": self.players[uid],
                    "text": f"{prefix}{uid}"
                },
                "style": "secondary"
            } for uid in self.alive
        ]

        return FlexMessage(
            alt_text=title,
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box", "layout": "vertical",
                    "paddingAll": "20px", "backgroundColor": c["bg"],
                    "contents": [
                        {"type": "text", "text": title,
                         "weight": "bold", "align": "center",
                         "color": c["primary"]},
                        {"type": "separator", "margin": "md"},
                        {"type": "box", "layout": "vertical",
                         "spacing": "sm", "contents": buttons}
                    ]
                }
            })
        )

    # =========================
    # ⛔ نهاية
    # =========================
    def end_mafia(self, result):
        self.phase = "end"
        return TextMessage(text=result)

    # =========================
    # تعطيل دوال BaseGame غير المستخدمة
    # =========================
    def get_question(self):
        return None

    def check_answer(self, user_answer, user_id, display_name):
        return None
