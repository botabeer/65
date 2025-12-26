from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
from threading import Timer
from typing import Dict, Any, Optional

class MafiaGame:
    def __init__(self, min_players=4, max_players=12):
        self.min_players = min_players
        self.max_players = max_players
        self.players: Dict[str, str] = {}  # player_id -> name
        self.roles: Dict[str, str] = {}    # player_id -> role
        self.alive_players: list = []
        self.mafia_members: list = []
        self.doctor: Optional[str] = None
        self.detective: Optional[str] = None
        self.night_actions: Dict[str, Any] = {}
        self.last_killed: Optional[str] = None
        self.last_saved: Optional[str] = None
        self.eliminated_player: Optional[str] = None
        self.current_round = 0
        self.game_active = False
        self.game_phase = "joining"  # joining, night, day
        self.roles_sent = False
        self.timer: Optional[Timer] = None

    # ==================== الرسائل ====================
    def handle_message(self, player_id, message):
        message = message.strip()
        if not self.game_active:
            return None

        if self.game_phase == "joining":
            if message == "انضم":
                return self.join_player(player_id)
            elif message == "ابدا":
                return self.start_actual_game()
            elif message == "ايقاف":
                return self.end_game()

        elif self.game_phase == "night":
            return self.handle_night_action(player_id, message)
        elif self.game_phase == "day":
            return self.handle_day_vote(player_id, message)
        return None

    def join_player(self, player_id):
        if len(self.players) >= self.max_players:
            return "عذرا، اللعبة ممتلئة"
        if player_id in self.players:
            return "أنت منضم بالفعل"
        self.players[player_id] = f"لاعب {len(self.players) + 1}"
        self.alive_players.append(player_id)
        return f"تم انضمام {self.players[player_id]}! ({len(self.players)}/{self.max_players})"

    def start_actual_game(self):
        if len(self.players) < self.min_players:
            return f"عدد اللاعبين غير كاف (الحد الأدنى {self.min_players})"
        self.assign_roles()
        self.send_roles_to_players()
        self.roles_sent = True
        self.current_round = 1
        self.game_phase = "night"
        self.game_active = True
        return self.night_phase()

    def end_game(self):
        self.__init__(self.min_players, self.max_players)
        return "تم إيقاف اللعبة وإعادة الضبط."

    # ==================== توزيع الأدوار ====================
    def assign_roles(self):
        import random
        p_ids = list(self.players.keys())
        random.shuffle(p_ids)
        mafia_count = max(1, len(p_ids)//4)
        self.mafia_members = p_ids[:mafia_count]
        for pid in self.mafia_members:
            self.roles[pid] = "مافيا"
        if len(p_ids) > mafia_count:
            self.doctor = p_ids[mafia_count]
            self.roles[self.doctor] = "دكتور"
        if len(p_ids) > mafia_count + 1:
            self.detective = p_ids[mafia_count+1]
            self.roles[self.detective] = "محقق"
        for pid in p_ids:
            if pid not in self.roles:
                self.roles[pid] = "مواطن"

    def send_roles_to_players(self):
        for pid, role in self.roles.items():
            print(f"[ROLE] {self.players[pid]} -> {role}")  # مؤقت للعرض

    # ==================== أفعال الليل ====================
    def handle_night_action(self, player_id, target_name):
        if player_id not in self.alive_players:
            return "أنت خارج اللعبة"

        target_id = None
        for pid, name in self.players.items():
            if name.lower() == target_name.lower() and pid in self.alive_players:
                target_id = pid
                break

        if not target_id:
            return "لاعب غير موجود أو متوفى"

        role = self.roles.get(player_id)
        if role == "مافيا" and player_id in self.mafia_members:
            self.night_actions["mafia"] = target_id
            return f"تم اختيار {target_name} للقتل"
        elif role == "دكتور" and player_id == self.doctor:
            self.night_actions["doctor"] = target_id
            self.last_saved = target_id
            return f"تم حماية {target_name}"
        elif role == "محقق" and player_id == self.detective:
            self.night_actions["detective"] = target_id
            investigated_role = self.roles.get(target_id, "مواطن")
            return f"{target_name} هو {investigated_role}"
        return "ليس لديك دور ليلي"

    # ==================== أفعال النهار ====================
    def handle_day_vote(self, player_id, target_name):
        if player_id not in self.alive_players:
            return "أنت خارج اللعبة"

        target_id = None
        for pid, name in self.players.items():
            if name.lower() == target_name.lower() and pid in self.alive_players:
                target_id = pid
                break

        if not target_id:
            return "لاعب غير موجود أو متوفى"

        self.vote_player(player_id, target_id)
        return f"تم التصويت لطرد {target_name}"

    def vote_player(self, voter_id, target_id):
        if not hasattr(self, "votes"):
            self.votes = {}
        self.votes[voter_id] = target_id

    # ==================== إكمال الليل ====================
    def complete_night(self):
        all_actions_done = (
            (not self.mafia_members or "mafia" in self.night_actions) and
            (not self.doctor or "doctor" in self.night_actions) and
            (not self.detective or "detective" in self.night_actions)
        )
        if not all_actions_done:
            return None

        self.process_night()
        result = self.check_game_over()
        if result:
            return self.get_game_over_screen(result)

        self.game_phase = "day"
        return self.get_night_result_screen()

    def process_night(self):
        mafia_target = self.night_actions.get("mafia")
        doctor_save = self.night_actions.get("doctor")
        if mafia_target and mafia_target != doctor_save:
            self.last_killed = mafia_target
            self.alive_players.remove(mafia_target)
        else:
            self.last_killed = None
        self.night_actions = {}

    # ==================== إكمال النهار ====================
    def complete_day(self):
        if hasattr(self, "votes"):
            from collections import Counter
            vote_counts = Counter(self.votes.values())
            if vote_counts:
                eliminated = max(vote_counts, key=vote_counts.get)
                self.eliminated_player = eliminated
                if eliminated in self.alive_players:
                    self.alive_players.remove(eliminated)
            else:
                self.eliminated_player = None
            self.votes = {}
        else:
            self.eliminated_player = None

        result = self.check_game_over()
        if result:
            return self.get_game_over_screen(result)

        self.current_round += 1
        self.game_phase = "night"
        return [self.get_day_result_screen(), self.night_phase()]

    # ==================== شاشات اللعبة ====================
    def get_theme_colors(self):
        return {
            "primary": "#1A1A1A",
            "text": "#2D2D2D",
            "success": "#10B981",
            "error": "#DC2626",
            "card": "#F3F4F6",
            "bg": "#FFFFFF",
            "border": "#D1D5DB"
        }

    def night_phase(self):
        self.timer = Timer(60, self.complete_night)
        self.timer.start()
        return "بدأت مرحلة الليل. أرسل دورك."

    def get_night_result_screen(self):
        c = self.get_theme_colors()
        killed_text = f"{self.players[self.last_killed]} قُتل" if self.last_killed else "لم يُقتل أحد"
        return FlexMessage(
            alt_text="نتيجة الليل",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {"type": "box", "layout": "vertical", "contents": [
                    {"type": "text", "text": f"الجولة {self.current_round}", "weight": "bold", "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": killed_text, "size": "lg", "color": c["error" if self.last_killed else "success"], "align": "center"}
                ], "paddingAll": "20px", "backgroundColor": c["bg"]}
            })
        )

    def get_day_result_screen(self):
        c = self.get_theme_colors()
        eliminated_text = f"{self.players[self.eliminated_player]} تم طرده" if self.eliminated_player else "لا يوجد تصويت كافي"
        return FlexMessage(
            alt_text="نتيجة النهار",
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "body": {"type": "box", "layout": "vertical", "contents": [
                    {"type": "text", "text": "نتيجة التصويت", "weight": "bold", "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": eliminated_text, "size": "lg", "color": c["error"], "align": "center"}
                ], "paddingAll": "20px", "backgroundColor": c["bg"]}
            })
        )

    def get_game_over_screen(self, winner):
        c = self.get_theme_colors()
        winner_color = c["success"] if "مواطن" in winner else c["error"]
        role_list = [{"type": "text", "text": f"{self.players[pid]}: {role}", "size": "sm", "color": c["text"], "margin": "xs"} for pid, role in self.roles.items()]
        return FlexMessage(
            alt_text=winner,
            contents=FlexContainer.from_dict({
                "type": "bubble",
                "size": "mega",
                "body": {"type": "box", "layout": "vertical", "contents": [
                    {"type": "text", "text": "انتهت اللعبة", "weight": "bold", "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": winner, "weight": "bold", "color": winner_color, "align": "center", "margin": "lg"},
                    {"type": "text", "text": "الأدوار:", "weight": "bold", "color": c["text"], "margin": "lg"},
                    {"type": "box", "layout": "vertical", "contents": role_list, "backgroundColor": c["card"], "paddingAll": "12px", "cornerRadius": "8px", "margin": "xs"}
                ], "paddingAll": "20px", "backgroundColor": c["bg"]},
                "footer": {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "button", "action": {"type": "message", "label": "لعبة جديدة", "text": "مافيا"}, "style": "primary", "height": "sm", "color": c["primary"]}
                ], "paddingAll": "12px", "backgroundColor": c["card"]}
            })
        )

    # ==================== تحقق من نهاية اللعبة ====================
    def check_game_over(self):
        mafia_alive = [pid for pid in self.mafia_members if pid in self.alive_players]
        citizens_alive = [pid for pid in self.alive_players if pid not in mafia_alive]

        if not mafia_alive:
            return "المواطنون فازوا"
        if len(mafia_alive) >= len(citizens_alive):
            return "المافيا فازت"
        return None
