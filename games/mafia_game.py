from games.base_game import BaseGame
import random

class MafiaGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=1, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme, game_type="social")
        self.game_name = "مافيا"
        self.supports_hint = False
        self.supports_reveal = False
        self.show_difficulty_progression = False
        
        self.min_players = 4
        self.max_players = 15
        self.players = {}
        self.roles = {}
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
    
    def start_game(self):
        self.game_active = True
        self.game_phase = "joining"
        self.current_round = 0
        self.players = {}
        self.roles = {}
        self.roles_sent = False
        return self.get_joining_screen()
    
    def get_joining_screen(self):
        c = self.get_theme_colors()
        joined = len(self.players)
        needed = max(0, self.min_players - joined)
        
        player_list = []
        for name in list(self.players.values())[:10]:
            player_list.append({
                "type": "text",
                "text": f"• {name}",
                "size": "xs",
                "color": c["text2"]
            })
        
        contents = [
            {"type": "text", "text": "لعبة المافيا", "size": "xxl", 
             "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "شرح اللعبة", 
                     "size": "sm", "weight": "bold", "color": c["text"]},
                    {"type": "text", 
                     "text": "لعبة جماعية تنقسم فيها الأدوار بين المافيا والمواطنين", 
                     "size": "xs", "color": c["text2"], "wrap": True, "margin": "xs"},
                    {"type": "text", 
                     "text": "• المافيا: يحاولون قتل المواطنين ليلاً\n• الدكتور: يحمي شخص واحد كل ليلة\n• المحقق: يتحقق من دور شخص كل ليلة\n• المواطنون: يصوتون لطرد المشتبه بهم نهاراً", 
                     "size": "xxs", "color": c["text3"], "wrap": True, "margin": "xs"}
                ],
                "backgroundColor": c["card"],
                "paddingAll": "12px",
                "cornerRadius": "8px",
                "margin": "md"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "ملاحظة مهمة", 
                     "size": "sm", "weight": "bold", "color": c["warning"]},
                    {"type": "text", 
                     "text": "يجب إضافة البوت كصديق ليصلك دورك بالخاص", 
                     "size": "xs", "color": c["text2"], "wrap": True, "margin": "xs"}
                ],
                "backgroundColor": c["card"],
                "paddingAll": "12px",
                "cornerRadius": "8px",
                "margin": "md",
                "borderWidth": "1px",
                "borderColor": c["warning"]
            },
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "اللاعبون", 
                             "size": "xs", "color": c["text3"]},
                            {"type": "text", "text": f"{joined}/{self.max_players}", 
                             "size": "xl", "weight": "bold", "color": c["primary"]}
                        ],
                        "flex": 1
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "مطلوب", 
                             "size": "xs", "color": c["text3"]},
                            {"type": "text", "text": str(needed) if needed > 0 else "جاهز", 
                             "size": "xl", "weight": "bold", 
                             "color": c["error"] if needed > 0 else c["success"]}
                        ],
                        "flex": 1
                    }
                ],
                "backgroundColor": c["card"],
                "paddingAll": "12px",
                "cornerRadius": "8px",
                "margin": "md"
            }
        ]
        
        if player_list:
            contents.extend([
                {"type": "text", "text": "المنضمون:", 
                 "size": "xs", "color": c["text3"], "margin": "md"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": player_list,
                    "backgroundColor": c["card"],
                    "paddingAll": "8px",
                    "cornerRadius": "8px",
                    "margin": "xs"
                }
            ])
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "انضمام", "text": "انضم"},
                        "style": "primary" if joined < self.max_players else "secondary",
                        "height": "sm",
                        "color": c["primary"] if joined < self.max_players else c["text3"]
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "بدء اللعبة", "text": "ابدأ"},
                        "style": "primary" if joined >= self.min_players else "secondary",
                        "height": "sm",
                        "color": c["success"] if joined >= self.min_players else c["text3"],
                        "margin": "sm"
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "إلغاء", "text": "ايقاف"},
                        "style": "secondary",
                        "height": "sm",
                        "color": c["text2"],
                        "margin": "sm"
                    }
                ],
                "paddingAll": "12px",
                "backgroundColor": c["card"]
            }
        }
        
        from linebot.v3.messaging import FlexMessage, FlexContainer
        return FlexMessage(alt_text="لعبة المافيا", contents=FlexContainer.from_dict(bubble))
    
    def assign_roles(self):
        player_list = list(self.players.keys())
        random.shuffle(player_list)
        num_players = len(player_list)
        
        num_mafia = max(1, num_players // 4)
        self.mafia_members = set(player_list[:num_mafia])
        remaining = player_list[num_mafia:]
        
        if len(remaining) >= 2:
            self.doctor = remaining[0]
            self.detective = remaining[1]
            self.citizens = set(remaining[2:])
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
    
    def send_roles_to_players(self, line_api):
        """إرسال الأدوار للاعبين عبر الرسائل الخاصة"""
        from linebot.v3.messaging import PushMessageRequest, TextMessage
        
        for player_id, role in self.roles.items():
            role_emoji = {"مافيا": "🔪", "دكتور": "💊", "محقق": "🔍", "مواطن": "👤"}
            
            if role == "مافيا":
                mafia_names = [self.players[p] for p in self.mafia_members if p != player_id]
                msg = f"{role_emoji.get(role, '')} دورك: {role}\n\nزملاؤك في المافيا: {', '.join(mafia_names) if mafia_names else 'أنت وحدك'}"
            else:
                msg = f"{role_emoji.get(role, '')} دورك: {role}"
            
            if role == "دكتور":
                msg += "\n\nفي كل ليلة، اكتب اسم شخص لحمايته"
            elif role == "محقق":
                msg += "\n\nفي كل ليلة، اكتب اسم شخص للتحقق من دوره"
            elif role == "مافيا":
                msg += "\n\nفي كل ليلة، اكتب اسم شخص لقتله"
            
            try:
                line_api.push_message(PushMessageRequest(
                    to=player_id,
                    messages=[TextMessage(text=msg)]
                ))
            except Exception as e:
                pass
    
    def get_night_phase_message(self):
        c = self.get_theme_colors()
        
        contents = [
            {"type": "text", "text": "الليل", "size": "xxl", 
             "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "text", "text": f"الجولة {self.current_round}", 
             "size": "sm", "color": c["text3"], "align": "center"},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {
                "type": "text",
                "text": "الجميع نائمون\nالمافيا والأدوار الخاصة يتحركون في الظلام",
                "size": "sm",
                "color": c["text2"],
                "wrap": True,
                "align": "center",
                "margin": "lg"
            },
            {
                "type": "text",
                "text": "تحقق من رسائلك الخاصة من البوت",
                "size": "xs",
                "color": c["warning"],
                "align": "center",
                "margin": "md"
            }
        ]
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            }
        }
        
        from linebot.v3.messaging import FlexMessage, FlexContainer
        return FlexMessage(alt_text="الليل", contents=FlexContainer.from_dict(bubble))
    
    def get_day_phase_message(self):
        c = self.get_theme_colors()
        
        alive_list = []
        for pid in self.alive_players:
            alive_list.append({
                "type": "text",
                "text": f"• {self.players[pid]}",
                "size": "xs",
                "color": c["text2"]
            })
        
        contents = [
            {"type": "text", "text": "النهار", "size": "xxl", 
             "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "text", "text": f"الجولة {self.current_round}", 
             "size": "sm", "color": c["text3"], "align": "center"},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        
        if self.last_killed:
            contents.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "خبر عاجل", 
                     "size": "sm", "weight": "bold", "color": c["error"]},
                    {"type": "text", 
                     "text": f"تم العثور على {self.players[self.last_killed]} قتيلاً", 
                     "size": "xs", "color": c["text2"], "wrap": True, "margin": "xs"}
                ],
                "backgroundColor": c["card"],
                "paddingAll": "12px",
                "cornerRadius": "8px",
                "margin": "md"
            })
        
        contents.extend([
            {"type": "text", "text": "الأحياء:", 
             "size": "xs", "color": c["text3"], "margin": "md"},
            {
                "type": "box",
                "layout": "vertical",
                "contents": alive_list,
                "backgroundColor": c["card"],
                "paddingAll": "8px",
                "cornerRadius": "8px",
                "margin": "xs"
            },
            {
                "type": "text",
                "text": "حان وقت التصويت لطرد المشتبه بهم\nاكتب اسم الشخص للتصويت عليه",
                "size": "sm",
                "color": c["text2"],
                "wrap": True,
                "align": "center",
                "margin": "lg"
            }
        ])
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            }
        }
        
        from linebot.v3.messaging import FlexMessage, FlexContainer
        return FlexMessage(alt_text="النهار", contents=FlexContainer.from_dict(bubble))
    
    def get_question(self):
        return self.get_joining_screen()
    
    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if self.game_phase == "joining":
            if normalized in ["انضم", "join"]:
                if user_id not in self.players and len(self.players) < self.max_players:
                    self.players[user_id] = display_name
                    return {
                        "response": self.get_joining_screen(),
                        "points": 0
                    }
            
            elif normalized in ["ابدأ", "start", "بدا"]:
                if len(self.players) >= self.min_players:
                    self.assign_roles()
                    self.game_phase = "night"
                    self.current_round = 1
                    
                    if not self.roles_sent:
                        self.send_roles_to_players(self.line_bot_api)
                        self.roles_sent = True
                    
                    return {
                        "response": self.get_night_phase_message(),
                        "points": 0
                    }
                else:
                    return {
                        "response": self.build_text_message(
                            f"نحتاج {self.min_players - len(self.players)} لاعبين إضافيين"
                        ),
                        "points": 0
                    }
        
        if normalized in ["ايقاف", "stop"]:
            return self.end_game()
        
        return None
    
    def end_game(self):
        self.game_active = False
        c = self.get_theme_colors()
        
        winner_team = None
        if not self.mafia_members.intersection(self.alive_players):
            winner_team = "المواطنون"
        elif len(self.mafia_members.intersection(self.alive_players)) >= len(self.alive_players) / 2:
            winner_team = "المافيا"
        
        contents = [
            {"type": "text", "text": "انتهت اللعبة", 
             "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        if winner_team:
            contents.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "الفائزون", 
                     "size": "sm", "color": c["success"], "align": "center"},
                    {"type": "text", "text": winner_team, 
                     "size": "xxl", "weight": "bold", "color": c["text"], 
                     "align": "center", "margin": "sm"}
                ],
                "backgroundColor": c["card"],
                "cornerRadius": "12px",
                "paddingAll": "16px",
                "margin": "md"
            })
        else:
            contents.append({
                "type": "text",
                "text": "تم إنهاء اللعبة مبكراً",
                "size": "md",
                "color": c["text2"],
                "align": "center",
                "margin": "lg"
            })
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "لعبة جديدة", "text": "مافيا"},
                        "style": "primary",
                        "height": "sm",
                        "color": c["primary"]
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "بداية", "text": "بداية"},
                        "style": "secondary",
                        "height": "sm",
                        "color": c["text2"]
                    }
                ],
                "spacing": "sm",
                "paddingAll": "12px",
                "backgroundColor": c["card"]
            }
        }
        
        from linebot.v3.messaging import FlexMessage, FlexContainer
        return {
            "game_over": True,
            "points": 0,
            "response": FlexMessage(alt_text="انتهت المافيا", 
                                   contents=FlexContainer.from_dict(bubble))
        }
