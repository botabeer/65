import random
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
from typing import Dict, Any, Optional

class MafiaGame:
    """لعبة المافيا - نسخة محسنة ومكتملة"""
    
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
        
        self.players: Dict[str, str] = {}  # {user_id: name}
        self.roles: Dict[str, str] = {}  # {user_id: role}
        self.alive_players: list = []
        self.mafia_members: list = []
        self.doctor: Optional[str] = None
        self.detective: Optional[str] = None
        self.night_actions: Dict[str, Any] = {}
        self.votes: Dict[str, str] = {}
        self.last_killed: Optional[str] = None
        self.eliminated_player: Optional[str] = None
        self.current_round = 0
        self.game_active = False
        self.game_phase = "joining"  # joining, night, day
        
    def get_theme_colors(self):
        themes = {
            "light": {
                "primary": "#1A1A1A", "text": "#2D2D2D", "success": "#2563EB",
                "error": "#EF4444", "card": "#F9FAFB", "bg": "#FFFFFF",
                "border": "#E5E7EB", "button": "#F5F5F5", "text2": "#6B7280"
            },
            "dark": {
                "primary": "#F9FAFB", "text": "#E5E7EB", "success": "#60A5FA",
                "error": "#F87171", "card": "#1F2937", "bg": "#111827",
                "border": "#374151", "button": "#F5F5F5", "text2": "#9CA3AF"
            }
        }
        return themes.get(self.theme, themes['light'])
    
    def start_game(self):
        """بداية اللعبة - شاشة الانضمام"""
        self.game_active = True
        self.game_phase = "joining"
        c = self.get_theme_colors()
        
        bubble = {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "لعبة المافيا", "size": "xl", "weight": "bold", 
                     "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "box", "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": f"اللاعبون: {len(self.players)}/{self.max_players}", 
                             "size": "lg", "color": c["text"], "align": "center"},
                            {"type": "text", "text": f"الحد الأدنى: {self.min_players} لاعبين", 
                             "size": "sm", "color": c["text2"], "align": "center", "margin": "sm"},
                            {"type": "text", "text": f"عدد المافيا: {self.mafia_count}", 
                             "size": "sm", "color": c["error"], "align": "center", "margin": "xs"}
                        ],
                        "backgroundColor": c["card"], "cornerRadius": "12px",
                        "paddingAll": "16px", "margin": "lg"
                    },
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {
                        "type": "text",
                        "text": "كيف تلعب:",
                        "size": "sm",
                        "weight": "bold",
                        "color": c["text"],
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "1. اضغط انضم للدخول للعبة\n2. عند اكتمال العدد اضغط ابدأ\n3. سيتم توزيع الأدوار سراً\n4. في الليل: المافيا تقتل، الدكتور يحمي\n5. في النهار: الجميع يصوت لطرد مشتبه",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "sm"
                    }
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
    
    def join_player(self, player_id, name):
        """انضمام لاعب"""
        if len(self.players) >= self.max_players:
            return f"عذراً، اللعبة ممتلئة ({self.max_players} لاعبين)"
        if player_id in self.players:
            return f"{name} منضم بالفعل"
        
        self.players[player_id] = name
        self.alive_players.append(player_id)
        return f"تم انضمام {name} ({len(self.players)}/{self.max_players})"
    
    def assign_roles(self):
        """توزيع الأدوار"""
        p_ids = list(self.players.keys())
        random.shuffle(p_ids)
        
        # المافيا
        self.mafia_members = p_ids[:self.mafia_count]
        for pid in self.mafia_members:
            self.roles[pid] = "مافيا"
        
        # الدكتور
        if len(p_ids) > self.mafia_count:
            self.doctor = p_ids[self.mafia_count]
            self.roles[self.doctor] = "دكتور"
        
        # المحقق
        if len(p_ids) > self.mafia_count + 1:
            self.detective = p_ids[self.mafia_count + 1]
            self.roles[self.detective] = "محقق"
        
        # المواطنون
        for pid in p_ids:
            if pid not in self.roles:
                self.roles[pid] = "مواطن"
    
    def start_actual_game(self):
        """بدء اللعبة الفعلية"""
        if len(self.players) < self.min_players:
            return f"عدد اللاعبين غير كاف (الحد الأدنى {self.min_players})"
        
        self.assign_roles()
        self.current_round = 1
        self.game_phase = "night"
        self.game_active = True
        
        # إرسال الأدوار للاعبين (في الواقع يجب إرسالها بالخاص)
        return self.night_phase()
    
    def night_phase(self):
        """مرحلة الليل"""
        c = self.get_theme_colors()
        
        bubble = {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"الليلة {self.current_round}", "size": "xl", 
                     "weight": "bold", "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "text",
                        "text": "حل الظلام على القرية...",
                        "size": "md",
                        "color": c["text"],
                        "align": "center",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "المافيا: اختاروا هدفكم", 
                             "size": "sm", "color": c["error"], "weight": "bold"},
                            {"type": "text", "text": "الدكتور: اختر من تحمي", 
                             "size": "sm", "color": c["success"], "weight": "bold", "margin": "sm"},
                            {"type": "text", "text": "المحقق: اختر من تحقق منه", 
                             "size": "sm", "color": c["text2"], "weight": "bold", "margin": "sm"}
                        ],
                        "backgroundColor": c["card"],
                        "cornerRadius": "12px",
                        "paddingAll": "16px",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "اكتب اسم اللاعب للتفاعل",
                        "size": "xs",
                        "color": c["text2"],
                        "align": "center",
                        "margin": "md"
                    }
                ],
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {"type": "button", "action": {"type": "message", "label": "تجاوز", "text": "تجاوز"},
                     "style": "secondary", "height": "sm", "color": c["button"]}
                ],
                "paddingAll": "12px",
                "backgroundColor": c["card"]
            }
        }
        
        return FlexMessage(alt_text="مرحلة الليل", contents=FlexContainer.from_dict(bubble))
    
    def get_night_result_screen(self):
        """شاشة نتيجة الليل"""
        c = self.get_theme_colors()
        
        if self.last_killed:
            killed_text = f"{self.players[self.last_killed]} قُتل في الليل"
            killed_color = c["error"]
        else:
            killed_text = "لم يُقتل أحد الليلة"
            killed_color = c["success"]
        
        alive_list = [
            {"type": "text", "text": f"• {self.players[pid]}", 
             "size": "xs", "color": c["text"]}
            for pid in self.alive_players
        ]
        
        bubble = {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "أشرقت الشمس", "weight": "bold", 
                     "size": "xl", "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": killed_text, "size": "lg", 
                             "color": killed_color, "align": "center", "weight": "bold"}
                        ],
                        "backgroundColor": c["card"],
                        "cornerRadius": "12px",
                        "paddingAll": "16px",
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {"type": "text", "text": "الأحياء:", "size": "sm", "weight": "bold", 
                     "color": c["text"], "margin": "md"},
                    {"type": "box", "layout": "vertical", "contents": alive_list, 
                     "margin": "xs", "spacing": "xs"}
                ],
                "paddingAll": "20px", "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box", "layout": "horizontal",
                "contents": [
                    {"type": "button", "action": {"type": "message", "label": "بدء التصويت", "text": "تصويت"},
                     "style": "secondary", "height": "sm", "color": c["button"]}
                ],
                "paddingAll": "12px", "backgroundColor": c["card"]
            }
        }
        
        return FlexMessage(alt_text="نتيجة الليل", contents=FlexContainer.from_dict(bubble))
    
    def get_day_result_screen(self):
        """شاشة نتيجة التصويت"""
        c = self.get_theme_colors()
        
        if self.eliminated_player:
            eliminated_name = self.players[self.eliminated_player]
            eliminated_role = self.roles[self.eliminated_player]
            result_text = f"تم طرد {eliminated_name}\nالدور: {eliminated_role}"
        else:
            result_text = "لم يكتمل التصويت"
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "نتيجة التصويت", "weight": "bold", 
                     "size": "xl", "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": result_text, "size": "lg", 
                             "color": c["error"], "align": "center", "wrap": True, "weight": "bold"}
                        ],
                        "backgroundColor": c["card"],
                        "cornerRadius": "12px",
                        "paddingAll": "16px",
                        "margin": "lg"
                    }
                ],
                "paddingAll": "20px", "backgroundColor": c["bg"]
            }
        }
        
        return FlexMessage(alt_text="نتيجة التصويت", contents=FlexContainer.from_dict(bubble))
    
    def get_game_over_screen(self, winner):
        """شاشة نهاية اللعبة"""
        c = self.get_theme_colors()
        winner_color = c["success"] if "مواطن" in winner else c["error"]
        
        role_list = [
            {"type": "text", "text": f"{self.players[pid]}: {role}", 
             "size": "xs", "color": c["text"], "margin": "xs"}
            for pid, role in self.roles.items()
        ]
        
        bubble = {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "انتهت اللعبة", "weight": "bold", 
                     "size": "xl", "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": winner, "weight": "bold", "size": "xxl",
                     "color": winner_color, "align": "center", "margin": "lg"},
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {"type": "text", "text": "الأدوار:", "weight": "bold", 
                     "size": "sm", "color": c["text"], "margin": "md"},
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
                     "style": "secondary", "height": "sm", "color": c["button"]},
                    {"type": "button", "action": {"type": "message", "label": "رجوع", "text": "بداية"},
                     "style": "secondary", "height": "sm", "color": c["button"]}
                ],
                "spacing": "sm", "paddingAll": "12px", "backgroundColor": c["card"]
            }
        }
        
        return FlexMessage(alt_text=winner, contents=FlexContainer.from_dict(bubble))
    
    def handle_night_action(self, player_id, target_name):
        """معالجة إجراء الليل"""
        if player_id not in self.alive_players:
            return "أنت خارج اللعبة"
        
        # البحث عن اللاعب المستهدف
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
            return f"المافيا اختارت {target_name}"
        elif role == "دكتور" and player_id == self.doctor:
            self.night_actions["doctor"] = target_id
            return f"الدكتور يحمي {target_name}"
        elif role == "محقق" and player_id == self.detective:
            investigated_role = self.roles.get(target_id, "مواطن")
            return f"{target_name} هو {investigated_role}"
        
        return "ليس لديك دور ليلي"
    
    def process_night(self):
        """معالجة أحداث الليل"""
        mafia_target = self.night_actions.get("mafia")
        doctor_save = self.night_actions.get("doctor")
        
        if mafia_target and mafia_target != doctor_save:
            self.last_killed = mafia_target
            if mafia_target in self.alive_players:
                self.alive_players.remove(mafia_target)
        else:
            self.last_killed = None
        
        self.night_actions = {}
    
    def handle_day_vote(self, player_id, target_name):
        """معالجة التصويت"""
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
    
    def process_day(self):
        """معالجة التصويت"""
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
    
    def check_game_over(self):
        """فحص نهاية اللعبة"""
        mafia_alive = [pid for pid in self.mafia_members if pid in self.alive_players]
        citizens_alive = [pid for pid in self.alive_players if pid not in mafia_alive]
        
        if not mafia_alive:
            return "المواطنون فازوا"
        if len(mafia_alive) >= len(citizens_alive):
            return "المافيا فازت"
        return None
    
    def get_question(self):
        """واجهة متوافقة مع BaseGame"""
        return self.start_game()
    
    def check_answer(self, user_answer, user_id, display_name):
        """معالجة الرسائل"""
        text = user_answer.strip()
        
        if self.game_phase == "joining":
            if text == "انضم":
                msg = self.join_player(user_id, display_name)
                return {"response": TextMessage(text=msg), "points": 0}
            elif text == "ابدا":
                result = self.start_actual_game()
                return {"response": result if isinstance(result, FlexMessage) else TextMessage(text=result), "points": 0}
            elif text in ["ايقاف", "ايقاف"]:
                self.__init__(self.line_bot_api, self.difficulty, self.theme)
                return {"response": TextMessage(text="تم إيقاف اللعبة"), "points": 0, "game_over": True}
        
        elif self.game_phase == "night":
            if text == "تجاوز":
                self.process_night()
                result = self.check_game_over()
                if result:
                    return {"response": self.get_game_over_screen(result), "points": 0, "game_over": True}
                self.game_phase = "day"
                return {"response": self.get_night_result_screen(), "points": 0}
            else:
                msg = self.handle_night_action(user_id, text)
                return {"response": TextMessage(text=msg), "points": 0}
        
        elif self.game_phase == "day":
            if text == "تصويت":
                return {"response": TextMessage(text="اكتب اسم اللاعب للتصويت"), "points": 0}
            elif text == "انهاء":
                self.process_day()
                result = self.check_game_over()
                if result:
                    return {"response": self.get_game_over_screen(result), "points": 0, "game_over": True}
                self.current_round += 1
                self.game_phase = "night"
                return {"response": self.night_phase(), "points": 0}
            else:
                msg = self.handle_day_vote(user_id, text)
                return {"response": TextMessage(text=msg), "points": 0}
        
        return None
