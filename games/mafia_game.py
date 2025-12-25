from games.base_game import BaseGame
import random

class MafiaGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme, game_type="competitive")
        self.game_name = "مافيا"
        self.supports_hint = False
        self.supports_reveal = False
        self.supports_difficulty = False
        self.show_progress = False
        
        self.min_players = 4
        self.max_players = 20
        self.players = {}
        self.roles = {}
        self.alive_players = set()
        self.dead_players = set()
        self.mafia_members = set()
        self.civilians = set()
        self.doctor = None
        self.detective = None
        self.game_phase = "waiting"
        self.current_round = 0
        self.night_actions = {}
        self.day_votes = {}

    def start_game(self):
        self.game_active = True
        self.game_phase = "joining"
        self.current_round = 0
        self.players = {}
        return self.get_joining_screen()

    def get_joining_screen(self):
        c = self.get_theme_colors()
        joined_count = len(self.players)
        
        contents = [
            {"type": "text", "text": "لعبة المافيا", "size": "xxl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "شرح اللعبة", "size": "md", "weight": "bold", "color": c["text"], "align": "center"},
                    {"type": "text", "text": "لعبة جماعية تنقسم فيها الادوار بين مافيا ومدنيين", "size": "xs", "color": c["text2"], "wrap": True, "margin": "sm"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": "الادوار", "size": "sm", "weight": "bold", "color": c["text"], "margin": "md"},
                    {
                        "type": "box", "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "مافيا: يحاولون قتل المدنيين", "size": "xs", "color": c["error"], "wrap": True},
                            {"type": "text", "text": "مدنيين: يصوتون لطرد المشتبهين", "size": "xs", "color": c["info"], "wrap": True, "margin": "xs"},
                            {"type": "text", "text": "دكتور: ينقذ لاعب واحد كل ليلة", "size": "xs", "color": c["success"], "wrap": True, "margin": "xs"},
                            {"type": "text", "text": "محقق: يكشف دور لاعب واحد", "size": "xs", "color": c["warning"], "wrap": True, "margin": "xs"}
                        ],
                        "margin": "sm"
                    }
                ],
                "backgroundColor": c["card"],
                "cornerRadius": "12px",
                "paddingAll": "16px",
                "borderWidth": "1px",
                "borderColor": c["border"],
                "margin": "md"
            },
            {
                "type": "box", "layout": "vertical",
                "contents": [
                    {
                        "type": "box", "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "اللاعبون المنضمون", "size": "sm", "weight": "bold", "color": c["text"], "flex": 1},
                            {"type": "text", "text": f"{joined_count}/{self.max_players}", "size": "lg", "weight": "bold", "color": c["primary"], "flex": 0}
                        ]
                    },
                    {"type": "text", "text": f"الحد الادنى: {self.min_players} لاعبين", "size": "xs", "color": c["text3"], "margin": "sm"}
                ],
                "backgroundColor": c["card"],
                "cornerRadius": "12px",
                "paddingAll": "12px",
                "margin": "lg"
            },
            {"type": "text", "text": "اكتب انضم للانضمام", "size": "sm", "color": c["text2"], "align": "center", "wrap": True, "margin": "lg"},
            {"type": "text", "text": "اكتب ابدأ لبدء اللعبة", "size": "sm", "color": c["success"], "align": "center", "wrap": True, "margin": "sm"}
        ]
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "24px",
                "backgroundColor": c["bg"]
            }
        }
        
        from linebot.v3.messaging import FlexMessage, FlexContainer
        return FlexMessage(alt_text=self.game_name, contents=FlexContainer.from_dict(bubble))

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
            self.civilians = set(remaining[2:])
        else:
            self.civilians = set(remaining)
        
        for player_id in self.mafia_members:
            self.roles[player_id] = "مافيا"
        if self.doctor:
            self.roles[self.doctor] = "دكتور"
        if self.detective:
            self.roles[self.detective] = "محقق"
        for player_id in self.civilians:
            self.roles[player_id] = "مدني"
        
        self.alive_players = set(player_list)

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
                        "response": self.build_text_message(f"{display_name} انضم للعبة\nالعدد الحالي: {len(self.players)}"),
                        "points": 0
                    }
            
            elif normalized in ["ابدأ", "start", "بدا"]:
                if len(self.players) >= self.min_players:
                    self.assign_roles()
                    self.game_phase = "night"
                    self.current_round = 1
                    return {
                        "response": self.build_text_message(f"بدأت اللعبة\nتم توزيع الادوار على {len(self.players)} لاعبين"),
                        "points": 0,
                        "game_over": False
                    }
                else:
                    needed = self.min_players - len(self.players)
                    return {
                        "response": self.build_text_message(f"نحتاج {needed} لاعبين اضافيين للبدء"),
                        "points": 0
                    }
        
        if normalized in ["ايقاف", "ايقاف"]:
            return self.end_game()
        
        return None
    
    def end_game(self):
        self.game_active = False
        c = self.get_theme_colors()
        
        contents = [
            {"type": "text", "text": "انتهت اللعبة", "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "text", "text": "شكرا للمشاركة", "size": "md", "color": c["text"], "align": "center", "margin": "lg"}
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
        return {
            "game_over": True,
            "points": 0,
            "response": FlexMessage(alt_text="انتهت اللعبة", contents=FlexContainer.from_dict(bubble))
        }
