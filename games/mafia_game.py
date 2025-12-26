from games.base_game import BaseGame
from linebot.v3.messaging import PushMessageRequest, TextMessage, FlexMessage, FlexContainer
import random

class MafiaGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=1, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme, game_type="social")
        self.game_name = "مافيا"
        self.min_players = 4
        self.max_players = 15
        self.players = {}  # player_id: name
        self.roles = {}    # player_id: role
        self.alive_players = set()
        self.dead_players = set()
        self.mafia_members = set()
        self.citizens = set()
        self.doctor = None
        self.detective = None
        self.game_phase = "waiting"
        self.current_round = 0
        self.night_actions = {}
        self.day_votes = {}
        self.last_killed = None
        self.last_saved = None
        self.last_investigated = None
        self.roles_sent = False
        self.eliminated_player = None
        self.game_active = False

    # ========================= شاشة الانضمام =========================
    def start_game(self):
        self.game_active = True
        self.game_phase = "joining"
        self.current_round = 0
        self.players = {}
        self.roles = {}
        self.roles_sent = False
        self.night_actions = {}
        self.day_votes = {}
        self.last_killed = None
        self.last_saved = None
        self.eliminated_player = None
        return self.get_joining_screen()

    def get_joining_screen(self):
        c = self.get_theme_colors()
        joined = len(self.players)
        player_list = [{"type": "text", "text": f"{i+1}. {name}", "size": "sm", "color": c["text"], "margin": "xs"}
                       for i, name in enumerate(list(self.players.values())[:10])]

        contents = [
            {"type": "text", "text": "لعبة المافيا", "size": "xxl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {"type": "box", "layout": "vertical", "contents": [
                {"type": "text", "text": "قواعد اللعبة", "size": "md", "weight": "bold", "color": c["text"], "margin": "md"},
                {"type": "text", "text": "المافيا: يحاولون قتل المواطنين في الليل", "size": "xs", "color": c["text2"], "wrap": True, "margin": "sm"},
                {"type": "text", "text": "الدكتور: يحمي شخصا واحدا كل ليلة", "size": "xs", "color": c["text2"], "wrap": True, "margin": "xs"},
                {"type": "text", "text": "المحقق: يتحقق من دور شخص واحد كل ليلة", "size": "xs", "color": c["text2"], "wrap": True, "margin": "xs"},
                {"type": "text", "text": "المواطنون: يصوتون لطرد المشتبه بهم", "size": "xs", "color": c["text2"], "wrap": True, "margin": "xs"}
            ], "backgroundColor": c["card"], "paddingAll": "12px", "cornerRadius": "8px", "margin": "md"}
        ]

        if player_list:
            contents.extend([
                {"type": "text", "text": "المنضمون:", "size": "sm", "weight": "bold", "color": c["text"], "margin": "lg"},
                {"type": "box", "layout": "vertical", "contents": player_list,
                 "backgroundColor": c["card"], "paddingAll": "12px", "cornerRadius": "8px", "margin": "xs"}
            ])

        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {"type": "box", "layout": "vertical", "contents": contents, "paddingAll": "20px", "backgroundColor": c["bg"]},
            "footer": {"type": "box", "layout": "vertical", "contents": [
                {"type": "button", "action": {"type": "message", "label": "انضمام للعبة", "text": "انضم"},
                 "style": "primary" if joined < self.max_players else "secondary", "height": "sm",
                 "color": c["primary"] if joined < self.max_players else c["text3"]},
                {"type": "button", "action": {"type": "message", "label": "بدء اللعبة", "text": "ابدا"},
                 "style": "primary" if joined >= self.min_players else "secondary", "height": "sm",
                 "color": c["success"] if joined >= self.min_players else c["text3"], "margin": "sm"},
                {"type": "button", "action": {"type": "message", "label": "الغاء اللعبة", "text": "ايقاف"},
                 "style": "secondary", "height": "sm", "color": c["error"], "margin": "sm"}
            ], "paddingAll": "12px", "backgroundColor": c["card"]}
        }

        return FlexMessage(alt_text="لعبة المافيا", contents=FlexContainer.from_dict(bubble))

    # ========================= توزيع الأدوار =========================
    def assign_roles(self):
        player_list = list(self.players.keys())
        random.shuffle(player_list)
        num_players = len(player_list)

        num_mafia = max(1, num_players // 5)
        self.mafia_members = set(player_list[:num_mafia])
        remaining = player_list[num_mafia:]

        if len(remaining) >= 2:
            self.doctor = remaining[0]
            self.detective = remaining[1]
            self.citizens = set(remaining[2:])
        elif len(remaining) == 1:
            self.doctor = remaining[0]
            self.citizens = set()
        else:
            self.citizens = set(remaining)

        for pid in self.mafia_members:
            self.roles[pid] = "مافيا"
        if self.doctor:
            self.roles[self.doctor] = "دكتور"
        if self.detective:
            self.roles[self.detective] = "محقق"
        for pid in self.citizens:
            self.roles[pid] = "مواطن"

        self.alive_players = set(player_list)
        self.dead_players = set()

    # ========================= إرسال الأدوار =========================
    def send_roles_to_players(self):
        c = self.get_theme_colors()
        for player_id, role in self.roles.items():
            contents = [
                {"type": "text", "text": "دورك في اللعبة", "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
                {"type": "separator", "margin": "md", "color": c["border"]},
                {"type": "box", "layout": "vertical", "contents": [
                    {"type": "text", "text": role, "size": "xxl", "weight": "bold", "color": c["success"], "align": "center"}
                ], "backgroundColor": c["card"], "paddingAll": "20px", "cornerRadius": "12px", "margin": "lg"}
            ]

            if role == "مافيا":
                mafia_names = [self.players[p] for p in self.mafia_members if p != player_id]
                if mafia_names:
                    contents.append({"type": "text", "text": "زملاؤك في المافيا: " + " - ".join(mafia_names),
                                     "size": "sm", "color": c["text2"], "wrap": True, "align": "center", "margin": "md"})
            elif role == "دكتور":
                contents.append({"type": "text", "text": "في كل ليلة اكتب اسم شخص لحمايته",
                                 "size": "xs", "color": c["text2"], "wrap": True, "align": "center", "margin": "md"})
            elif role == "محقق":
                contents.append({"type": "text", "text": "في كل ليلة اكتب اسم شخص للتحقق من دوره",
                                 "size": "xs", "color": c["text2"], "wrap": True, "align": "center", "margin": "md"})
            elif role == "مواطن":
                contents.append({"type": "text", "text": "هدفك اكتشاف المافيا والتصويت لطردهم في النهار",
                                 "size": "xs", "color": c["text2"], "wrap": True, "align": "center", "margin": "md"})

            bubble = {"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": contents,
                                                 "paddingAll": "20px", "backgroundColor": c["bg"]}}
            try:
                self.line_bot_api.push_message(PushMessageRequest(
                    to=player_id,
                    messages=[FlexMessage(alt_text=f"دورك: {role}", contents=FlexContainer.from_dict(bubble))]
                ))
            except Exception:
                pass

    # ========================= المرحلة الليلية =========================
    def night_phase(self):
        self.game_phase = "night"
        self.night_actions = {"mafia": None, "doctor": None, "detective": None}
        return "الليل بدأ: ارسل أدواركم (المافيا، الدكتور، المحقق)"

    # ========================= المرحلة النهارية =========================
    def day_phase(self):
        self.game_phase = "day"
        self.day_votes = {}
        return "النهار بدأ: صوت لطرد المشتبه بهم"

    # ========================= عمليات التصويت =========================
    def vote_player(self, voter_id, target_id):
        if self.game_phase != "day" or voter_id not in self.alive_players:
            return
        self.day_votes[target_id] = self.day_votes.get(target_id, 0) + 1

    # ========================= معالجة الليل =========================
    def process_night(self):
        killed = self.night_actions.get("mafia")
        saved = self.night_actions.get("doctor")

        if killed and killed != saved:
            self.alive_players.discard(killed)
            self.dead_players.add(killed)
            self.last_killed = killed
        else:
            self.last_killed = None

        investigated = self.night_actions.get("detective")
        self.last_investigated = investigated

    # ========================= معالجة النهار =========================
    def process_day(self):
        if not self.day_votes:
            return None
        max_votes = max(self.day_votes.values())
        candidates = [p for p, v in self.day_votes.items() if v == max_votes]
        eliminated = random.choice(candidates)
        self.alive_players.discard(eliminated)
        self.dead_players.add(eliminated)
        self.eliminated_player = eliminated
        return eliminated

    # ========================= التحقق من انتهاء اللعبة =========================
    def check_game_over(self):
        mafia_alive = len(self.mafia_members & self.alive_players)
        citizens_alive = len(self.alive_players - self.mafia_members)
        if mafia_alive == 0:
            return "المواطنون فازوا"
        elif mafia_alive >= citizens_alive:
            return "المافيا فازت"
        return None

    # ========================= إنهاء اللعبة =========================
    def end_game(self):
        self.game_active = False
        c = self.get_theme_colors()
        contents = [
            {"type": "text", "text": "تم إنهاء اللعبة", "size": "xl", "weight": "bold", "color": c["error"], "align": "center"},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {"type": "text", "text": "شكرا للعب!", "size": "sm", "color": c["text2"], "align": "center", "margin": "lg"}
        ]
        bubble = {"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": contents,
                                             "paddingAll": "20px", "backgroundColor": c["bg"]},
                  "footer": {"type": "box", "layout": "horizontal", "contents": [
                      {"type": "button", "action": {"type": "message", "label": "لعبة جديدة", "text": "مافيا"},
                       "style": "primary", "height": "sm", "color": c["primary"]}
                  ], "paddingAll": "12px", "backgroundColor": c["card"]}}
        return FlexMessage(alt_text="تم إنهاء اللعبة", contents=FlexContainer.from_dict(bubble))
