from linebot.v3.messaging import FlexMessage, FlexContainer, TextMessage
import random
from collections import Counter


class MafiaGame:
    def __init__(self, line_bot_api, theme="light"):
        self.api = line_bot_api
        self.theme = theme
        self.game_name = "مافيا"

        self.min_players = 4
        self.max_players = 15

        self.players = {}     # user_id -> name
        self.roles = {}       # user_id -> role
        self.alive = []

        self.mafia = []
        self.doctor = None
        self.detective = None

        self.phase = "joining"   # joining / night / day
        self.round = 0

        self.night_actions = {}
        self.votes = {}

    # ======================
    # 🎨 الثيم
    # ======================
    def colors(self):
        themes = {
            "light": {
                "bg": "#FFFFFF", "card": "#F9FAFB", "border": "#E5E7EB",
                "text": "#1F2937", "sub": "#6B7280",
                "success": "#10B981", "danger": "#EF4444",
                "btn": "#F5F5F5"
            },
            "dark": {
                "bg": "#111827", "card": "#1F2937", "border": "#374151",
                "text": "#F9FAFB", "sub": "#9CA3AF",
                "success": "#34D399", "danger": "#F87171",
                "btn": "#374151"
            }
        }
        return themes.get(self.theme, themes["light"])

    # ======================
    # 🎮 Router موحد
    # ======================
    def handle(self, user_id, user_name, text):
        if text == "mafia_join":
            return self.join(user_id, user_name)
        if text == "mafia_start":
            return self.start()
        if text == "mafia_end":
            return self.end()
        if text.startswith("mafia_night_"):
            return self.night_action(user_id, text.replace("mafia_night_", ""))
        if text.startswith("mafia_vote_"):
            return self.vote(user_id, text.replace("mafia_vote_", ""))
        return None

    # ======================
    # 🚪 الانضمام
    # ======================
    def join(self, uid, name):
        if uid not in self.players and len(self.players) < self.max_players:
            self.players[uid] = name
            self.alive.append(uid)
        return self.lobby()

    # ======================
    # 🎭 توزيع الأدوار + إرسال خاص
    # ======================
    def assign_roles(self):
        ids = list(self.players.keys())
        random.shuffle(ids)

        self.mafia = ids[:1]
        self.doctor = ids[1]
        self.detective = ids[2]

        for uid in ids:
            if uid in self.mafia:
                self.roles[uid] = "مافيا"
            elif uid == self.doctor:
                self.roles[uid] = "دكتور"
            elif uid == self.detective:
                self.roles[uid] = "محقق"
            else:
                self.roles[uid] = "مواطن"

        self.send_roles_private()

    def send_roles_private(self):
        for uid, role in self.roles.items():
            self.api.push_message(
                uid,
                TextMessage(text=f"دورك في لعبة المافيا هو: {role}")
            )

    # ======================
    # 🏠 الواجهة الرئيسية
    # ======================
    def lobby(self):
        c = self.colors()
        return FlexMessage(
            alt_text="لعبة المافيا",
            contents=FlexContainer.from_dict({
                "type": "bubble", "size": "mega",
                "body": {
                    "type": "box", "layout": "vertical",
                    "paddingAll": "20px", "backgroundColor": c["bg"],
                    "contents": [
                        {"type": "text", "text": "لعبة المافيا",
                         "weight": "bold", "size": "xl",
                         "align": "center", "color": c["text"]},
                        {"type": "separator", "margin": "md", "color": c["border"]},
                        {
                            "type": "box", "layout": "vertical",
                            "margin": "lg", "paddingAll": "12px",
                            "backgroundColor": c["card"], "cornerRadius": "10px",
                            "contents": [
                                {"type": "text", "text": "شرح مختصر",
                                 "weight": "bold", "color": c["text"]},
                                {"type": "text", "size": "sm", "wrap": True,
                                 "color": c["sub"],
                                 "text": "المافيا تقتل ليلاً\nالدكتور يحمي\nالمحقق يحقق\nالنهار للتصويت"}
                            ]
                        },
                        {"type": "text",
                         "text": f"اللاعبون: {len(self.players)}/{self.max_players}",
                         "align": "center", "margin": "lg", "color": c["text"]}
                    ]
                },
                "footer": {
                    "type": "box", "layout": "vertical", "spacing": "sm",
                    "contents": [
                        {"type": "button", "style": "secondary", "color": c["btn"],
                         "action": {"type": "message", "label": "انضمام", "text": "mafia_join"}},
                        {"type": "button", "style": "secondary", "color": c["btn"],
                         "action": {"type": "message", "label": "بدء اللعبة", "text": "mafia_start"}},
                        {"type": "button", "style": "secondary", "color": c["btn"],
                         "action": {"type": "message", "label": "إلغاء", "text": "mafia_end"}}
                    ]
                }
            })
        )

    # ======================
    # ▶️ بدء
    # ======================
    def start(self):
        if len(self.players) < self.min_players:
            return TextMessage(text="عدد اللاعبين غير كاف")

        self.assign_roles()
        self.phase = "night"
        self.round = 1
        return self.player_buttons("مرحلة الليل", "mafia_night_")

    # ======================
    # 🌙 الليل
    # ======================
    def night_action(self, uid, target):
        if uid not in self.alive:
            return None

        role = self.roles.get(uid)
        if role == "مافيا":
            self.night_actions["mafia"] = target
        elif role == "دكتور":
            self.night_actions["doctor"] = target

        if "mafia" in self.night_actions and "doctor" in self.night_actions:
            return self.resolve_night()
        return None

    def resolve_night(self):
        target = self.night_actions.get("mafia")
        saved = self.night_actions.get("doctor")

        if target and target != saved and target in self.alive:
            self.alive.remove(target)

        self.night_actions = {}
        self.phase = "day"
        return self.player_buttons("مرحلة التصويت", "mafia_vote_")

    # ======================
    # ☀️ النهار
    # ======================
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
        return self.check_game()

    # ======================
    # 🏁 الفوز
    # ======================
    def check_game(self):
        mafia_alive = [m for m in self.mafia if m in self.alive]
        citizens = [p for p in self.alive if p not in mafia_alive]

        if not mafia_alive:
            return self.end_screen("المواطنون فازوا")
        if len(mafia_alive) >= len(citizens):
            return self.end_screen("المافيا فازت")

        self.phase = "night"
        return self.player_buttons("مرحلة الليل", "mafia_night_")

    # ======================
    # 🔘 أزرار اللاعبين
    # ======================
    def player_buttons(self, title, prefix):
        c = self.colors()
        buttons = [{
            "type": "button", "style": "secondary", "color": c["btn"],
            "action": {"type": "message", "label": self.players[u], "text": f"{prefix}{u}"}
        } for u in self.alive]

        return FlexMessage(
            alt_text=title,
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {
                    "type": "box", "layout": "vertical",
                    "paddingAll": "20px", "backgroundColor": c["bg"],
                    "contents": [
                        {"type": "text", "text": title,
                         "weight": "bold", "size": "lg",
                         "align": "center", "color": c["text"]},
                        {"type": "separator", "margin": "md", "color": c["border"]},
                        {"type": "box", "layout": "vertical",
                         "spacing": "sm", "contents": buttons}
                    ]
                }
            })
        )

    # ======================
    # 🧱 النهاية
    # ======================
    def end_screen(self, result):
        c = self.colors()
        roles = [
            {"type": "text", "size": "sm", "color": c["text"],
             "text": f"{self.players[u]} : {self.roles[u]}"}
            for u in self.roles
        ]

        return FlexMessage(
            alt_text="انتهت اللعبة",
            contents=FlexContainer.from_dict({
                "type": "bubble", "size": "mega",
                "body": {
                    "type": "box", "layout": "vertical",
                    "paddingAll": "20px", "backgroundColor": c["bg"],
                    "contents": [
                        {"type": "text", "text": "انتهت اللعبة",
                         "weight": "bold", "size": "xl",
                         "align": "center", "color": c["text"]},
                        {"type": "separator", "margin": "md", "color": c["border"]},
                        {"type": "text", "text": result,
                         "align": "center", "size": "lg",
                         "margin": "lg",
                         "color": c["success"] if "المواطن" in result else c["danger"]},
                        {"type": "separator", "margin": "lg", "color": c["border"]},
                        {"type": "box", "layout": "vertical", "spacing": "xs", "contents": roles}
                    ]
                }
            })
        )

    # ======================
    # ⛔ إيقاف
    # ======================
    def end(self):
        self.__init__(self.api, self.theme)
        return TextMessage(text="تم إنهاء اللعبة")
