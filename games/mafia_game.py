from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
from typing import Dict, Any, Optional
import random

class MafiaGame:
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        self.line_bot_api = line_bot_api
        self.difficulty = difficulty
        self.theme = theme
        self.game_name = "مافيا"
        
        # تحديد الإعدادات حسب الصعوبة
        if difficulty <= 2:  # سهل
            self.min_players, self.max_players, self.mafia_count = 4, 8, 1
        elif difficulty <= 3:  # متوسط
            self.min_players, self.max_players, self.mafia_count = 5, 10, 2
        else:  # صعب
            self.min_players, self.max_players, self.mafia_count = 6, 12, 3
        
        self.players: Dict[str, str] = {}
        self.roles: Dict[str, str] = {}
        self.alive_players: list = []
        self.mafia_members: list = []
        self.doctor: Optional[str] = None
        self.detective: Optional[str] = None
        self.night_actions: Dict[str, Any] = {}
        self.votes: Dict[str, str] = {}
        self.last_killed: Optional[str] = None
        self.last_saved: Optional[str] = None
        self.eliminated_player: Optional[str] = None
        self.current_round = 0
        self.game_active = False
        self.game_phase = "joining"
    
    def get_theme_colors(self):
        themes = {
            "light": {"primary": "#1A1A1A", "text": "#2D2D2D", "success": "#10B981",
                     "error": "#EF4444", "card": "#F9FAFB", "bg": "#FFFFFF",
                     "border": "#E5E7EB", "button": "#F5F5F5", "text2": "#6B7280"},
            "dark": {"primary": "#F9FAFB", "text": "#E5E7EB", "success": "#34D399",
                    "error": "#F87171", "card": "#1F2937", "bg": "#111827",
                    "border": "#374151", "button": "#F5F5F5", "text2": "#9CA3AF"}
        }
        return themes.get(self.theme, themes['light'])
    
    def join_player(self, player_id, name=None):
        if len(self.players) >= self.max_players:
            return "عذراً، اللعبة ممتلئة"
        if player_id in self.players:
            return "أنت منضم بالفعل"
        
        if not name:
            name = f"لاعب {len(self.players) + 1}"
        
        self.players[player_id] = name
        self.alive_players.append(player_id)
        return f"تم انضمام {name} ({len(self.players)}/{self.max_players})"
    
    def assign_roles(self):
        p_ids = list(self.players.keys())
        random.shuffle(p_ids)
        
        # تعيين المافيا
        self.mafia_members = p_ids[:self.mafia_count]
        for pid in self.mafia_members:
            self.roles[pid] = "مافيا"
        
        # تعيين الدكتور
        if len(p_ids) > self.mafia_count:
            self.doctor = p_ids[self.mafia_count]
            self.roles[self.doctor] = "دكتور"
        
        # تعيين المحقق
        if len(p_ids) > self.mafia_count + 1:
            self.detective = p_ids[self.mafia_count + 1]
            self.roles[self.detective] = "محقق"
        
        # باقي اللاعبين مواطنون
        for pid in p_ids:
            if pid not in self.roles:
                self.roles[pid] = "مواطن"
    
    def handle_message(self, player_id, message):
        message = message.strip()
        
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
    
    def handle_night_action(self, player_id, target_name):
        if player_id not in self.alive_players:
            return "أنت خارج اللعبة"
        
        target_id = None
        for pid, name in self.players.items():
            if name.lower() == target_name.lower() and pid in self.alive_players:
                target_id = pid
                break
        
        if not target_id:
            return "لاعب غير موجود"
        
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
    
    def handle_day_vote(self, player_id, target_name):
        if player_id not in self.alive_players:
            return "أنت خارج اللعبة"
        
        target_id = None
        for pid, name in self.players.items():
            if name.lower() == target_name.lower() and pid in self.alive_players:
                target_id = pid
                break
        
        if not target_id:
            return "لاعب غير موجود"
        
        self.votes[player_id] = target_id
        return f"تم التصويت لطرد {target_name}"
    
    def complete_night(self):
        all_done = (
            (not self.mafia_members or "mafia" in self.night_actions) and
            (not self.doctor or "doctor" in self.night_actions) and
            (not self.detective or "detective" in self.night_actions)
        )
        
        if not all_done:
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
            if mafia_target in self.alive_players:
                self.alive_players.remove(mafia_target)
        else:
            self.last_killed = None
        
        self.night_actions = {}
    
    def complete_day(self):
        if self.votes:
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
    
    def check_game_over(self):
        mafia_alive = [pid for pid in self.mafia_members if pid in self.alive_players]
        citizens_alive = [pid for pid in self.alive_players if pid not in mafia_alive]
        
        if not mafia_alive:
            return "المواطنون فازوا"
        if len(mafia_alive) >= len(citizens_alive):
            return "المافيا فازت"
        return None
    
    def start_game(self):
        c = self.get_theme_colors()
        self.game_active = True
        self.game_phase = "joining"
        
        bubble = {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "لعبة المافيا", "size": "xl", "weight": "bold", 
                     "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": f"اللاعبون: {len(self.players)}/{self.max_players}", 
                     "size": "lg", "color": c["text"], "align": "center", "margin": "lg"},
                    {"type": "text", "text": f"الحد الأدنى: {self.min_players} لاعبين", 
                     "size": "sm", "color": c["text2"], "align": "center", "margin": "sm"},
                    {"type": "text", "text": f"عدد المافيا: {self.mafia_count}", 
                     "size": "sm", "color": c["error"], "align": "center", "margin": "xs"}
                ],
                "paddingAll": "20px", "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box", "layout": "horizontal",
                "contents": [
                    {"type": "button", "action": {"type": "message", "label": "انضم", "text": "انضم"},
                     "style": "secondary", "height": "sm", "color": c["button"], "flex": 1},
                    {"type": "button", "action": {"type": "message", "label": "ابدأ", "text": "ابدا"},
                     "style": "secondary", "height": "sm", "color": c["button"], "flex": 1},
                    {"type": "button", "action": {"type": "message", "label": "إيقاف", "text": "ايقاف"},
                     "style": "secondary", "height": "sm", "color": c["button"], "flex": 1}
                ],
                "spacing": "sm", "paddingAll": "12px", "backgroundColor": c["card"]
            }
        }
        
        return FlexMessage(alt_text="لعبة المافيا", contents=FlexContainer.from_dict(bubble))
    
    def start_actual_game(self):
        if len(self.players) < self.min_players:
            return f"عدد اللاعبين غير كاف (الحد الأدنى {self.min_players})"
        
        self.assign_roles()
        self.current_round = 1
        self.game_phase = "night"
        self.game_active = True
        
        return self.night_phase()
    
    def night_phase(self):
        return "بدأت مرحلة الليل. اكتب اسم اللاعب للتفاعل"
    
    def get_night_result_screen(self):
        c = self.get_theme_colors()
        killed_text = f"{self.players[self.last_killed]} قُتل" if self.last_killed else "لم يُقتل أحد"
        
        alive_list = [{"type": "text", "text": self.players[pid], "size": "xs", "color": c["text"]} 
                      for pid in self.alive_players]
        
        bubble = {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"الجولة {self.current_round}", "weight": "bold", 
                     "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": killed_text, "size": "lg", 
                     "color": c["error"] if self.last_killed else c["success"], "align": "center", "margin": "md"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": "اللاعبون الأحياء:", "size": "sm", "weight": "bold", 
                     "color": c["text"], "margin": "md"},
                    {"type": "box", "layout": "vertical", "contents": alive_list, "margin": "xs"}
                ],
                "paddingAll": "20px", "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box", "layout": "horizontal",
                "contents": [
                    {"type": "button", "action": {"type": "message", "label": "التصويت", "text": "تصويت"},
                     "style": "secondary", "height": "sm", "color": c["button"]}
                ],
                "paddingAll": "12px", "backgroundColor": c["card"]
            }
        }
        
        return FlexMessage(alt_text="نتيجة الليل", contents=FlexContainer.from_dict(bubble))
    
    def get_day_result_screen(self):
        c = self.get_theme_colors()
        
        if self.eliminated_player:
            eliminated_name = self.players[self.eliminated_player]
            eliminated_role = self.roles[self.eliminated_player]
            eliminated_text = f"{eliminated_name} تم طرده\nالدور: {eliminated_role}"
        else:
            eliminated_text = "لا يوجد تصويت كافي"
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "نتيجة التصويت", "weight": "bold", 
                     "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": eliminated_text, "size": "lg", 
                     "color": c["error"], "align": "center", "margin": "md", "wrap": True}
                ],
                "paddingAll": "20px", "backgroundColor": c["bg"]
            }
        }
        
        return FlexMessage(alt_text="نتيجة النهار", contents=FlexContainer.from_dict(bubble))
    
    def get_game_over_screen(self, winner):
        c = self.get_theme_colors()
        winner_color = c["success"] if "مواطن" in winner else c["error"]
        
        role_list = [{"type": "text", "text": f"{self.players[pid]}: {role}", 
                     "size": "sm", "color": c["text"], "margin": "xs"} 
                    for pid, role in self.roles.items()]
        
        bubble = {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "انتهت اللعبة", "weight": "bold", 
                     "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": winner, "weight": "bold", "size": "xl",
                     "color": winner_color, "align": "center", "margin": "lg"},
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {"type": "text", "text": "الأدوار:", "weight": "bold", 
                     "color": c["text"], "margin": "md"},
                    {"type": "box", "layout": "vertical", "contents": role_list,
                     "backgroundColor": c["card"], "paddingAll": "12px", 
                     "cornerRadius": "8px", "margin": "xs"}
                ],
                "paddingAll": "20px", "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box", "layout": "horizontal",
                "contents": [
                    {"type": "button", "action": {"type": "message", "label": "لعبة جديدة", "text": "مافيا"},
                     "style": "secondary", "height": "sm", "color": c["button"]}
                ],
                "paddingAll": "12px", "backgroundColor": c["card"]
            }
        }
        
        return FlexMessage(alt_text=winner, contents=FlexContainer.from_dict(bubble))
    
    def end_game(self):
        self.__init__(self.line_bot_api, self.difficulty, self.theme)
        return "تم إيقاف اللعبة وإعادة الضبط"
    
    def get_question(self):
        return self.start_game()
    
    def check_answer(self, user_answer, user_id, display_name):
        result = self.handle_message(user_id, user_answer)
        
        if result:
            return {
                "response": TextMessage(text=result) if isinstance(result, str) else result,
                "points": 0
            }
        
        return None
