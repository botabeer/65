from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import re
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class BaseGame(ABC):
    THEMES = {
        "light": {
            "primary": "#000000",
            "text": "#1A1A1A",
            "text2": "#4B5563",
            "text3": "#9CA3AF",
            "bg": "#FFFFFF",
            "card": "#F8F9FA",
            "border": "#E5E7EB",
            "success": "#059669",
            "warning": "#D97706",
            "error": "#DC2626"
        },
        "dark": {
            "primary": "#FFFFFF",
            "text": "#F9FAFB",
            "text2": "#D1D5DB",
            "text3": "#9CA3AF",
            "bg": "#0F172A",
            "card": "#1E293B",
            "border": "#334155",
            "success": "#10B981",
            "warning": "#F59E0B",
            "error": "#EF4444"
        }
    }
    
    def __init__(self, line_bot_api, difficulty=1, theme="light", game_type="competitive"):
        self.line_bot_api = line_bot_api
        self.base_difficulty = difficulty
        self.current_difficulty = 1
        self.theme = theme
        self.game_type = game_type
        self.game_name = "لعبة"
        
        self.total_rounds = 5
        self.current_question = 0
        self.game_active = False
        
        self.scores = {}
        self.answered_users = set()
        self.withdrawn_users = set()
        
        self.current_answer = None
        self.previous_answer = None
        self.start_time = None
        self.round_start_time = None
        
        self.supports_hint = True
        self.supports_reveal = True
        self.show_difficulty_progression = True
    
    def get_current_difficulty_level(self):
        """حساب مستوى الصعوبة الحالي بناء على الجولة"""
        if self.current_question == 0:
            return 1
        elif self.current_question == 1:
            return 2
        elif self.current_question == 2:
            return 3
        elif self.current_question == 3:
            return 4
        else:
            return 5
    
    def get_difficulty_config(self):
        """الحصول على إعدادات الصعوبة الحالية"""
        level = self.get_current_difficulty_level()
        configs = {
            1: {"name": "سهل جداً", "time": 30, "hint_cost": 0},
            2: {"name": "سهل", "time": 25, "hint_cost": 0},
            3: {"name": "متوسط", "time": 20, "hint_cost": 1},
            4: {"name": "صعب", "time": 15, "hint_cost": 2},
            5: {"name": "صعب جداً", "time": 10, "hint_cost": 3}
        }
        return configs.get(level, configs[3])
    
    def normalize_text(self, text):
        if not text:
            return ""
        text = str(text).strip().lower()
        trans = str.maketrans({
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا',
            'ؤ': 'و', 'ئ': 'ي', 'ء': '',
            'ة': 'ه', 'ى': 'ي'
        })
        text = text.translate(trans)
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        return re.sub(r'\s+', ' ', text).strip()
    
    def add_score(self, user_id, display_name, points=1):
        if user_id in self.withdrawn_users:
            return 0
        if user_id not in self.scores:
            self.scores[user_id] = {'name': display_name, 'score': 0, 'correct': 0}
        self.scores[user_id]['score'] += points
        self.scores[user_id]['correct'] += 1
        return points
    
    def get_theme_colors(self):
        return self.THEMES.get(self.theme, self.THEMES['light'])
    
    def create_difficulty_indicator(self):
        """مؤشر مستوى الصعوبة"""
        c = self.get_theme_colors()
        level = self.get_current_difficulty_level()
        config = self.get_difficulty_config()
        
        circles = []
        for i in range(1, 6):
            circles.append({
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "width": "12px",
                "height": "12px",
                "cornerRadius": "6px",
                "backgroundColor": c["primary"] if i <= level else c["border"]
            })
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": circles,
                    "spacing": "xs",
                    "justifyContent": "center"
                },
                {
                    "type": "text",
                    "text": f"المستوى: {config['name']}",
                    "size": "xxs",
                    "color": c["text3"],
                    "align": "center",
                    "margin": "xs"
                }
            ],
            "margin": "md"
        }
    
    def create_progress_bar(self):
        """شريط التقدم"""
        c = self.get_theme_colors()
        progress = int((self.current_question / self.total_rounds) * 100)
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": f"الجولة {self.current_question + 1}/{self.total_rounds}", 
                         "size": "xs", "color": c["text2"], "flex": 1},
                        {"type": "text", "text": f"{progress}%", 
                         "size": "xs", "color": c["text2"], "align": "end", "flex": 0}
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [],
                            "width": f"{progress}%",
                            "height": "4px",
                            "backgroundColor": c["primary"],
                            "cornerRadius": "2px"
                        }
                    ],
                    "height": "4px",
                    "backgroundColor": c["border"],
                    "cornerRadius": "2px",
                    "margin": "sm"
                }
            ],
            "margin": "md"
        }
    
    def build_question_message(self, question_text, subtitle=None):
        c = self.get_theme_colors()
        
        contents = [
            {"type": "text", "text": self.game_name, "size": "xl", "weight": "bold", 
             "color": c["primary"], "align": "center"}
        ]
        
        contents.append(self.create_progress_bar())
        
        if self.show_difficulty_progression:
            contents.append(self.create_difficulty_indicator())
        
        contents.append({"type": "separator", "margin": "md", "color": c["border"]})
        
        if self.previous_answer and self.current_question > 0:
            contents.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "الإجابة السابقة:", 
                     "size": "xxs", "color": c["text3"]},
                    {"type": "text", "text": str(self.previous_answer), 
                     "size": "xs", "color": c["text2"], "wrap": True, "margin": "xs"}
                ],
                "backgroundColor": c["card"],
                "paddingAll": "8px",
                "cornerRadius": "8px",
                "margin": "md"
            })
        
        contents.append({
            "type": "text", "text": question_text, "size": "md", 
            "wrap": True, "color": c["text"], "align": "center", "margin": "lg"
        })
        
        if subtitle:
            contents.append({
                "type": "text", "text": subtitle, "size": "xs", 
                "color": c["text2"], "align": "center", "margin": "sm", "wrap": True
            })
        
        footer_buttons = []
        if self.supports_hint:
            footer_buttons.append({
                "type": "button",
                "action": {"type": "message", "label": "تلميح", "text": "لمح"},
                "style": "secondary",
                "height": "sm",
                "color": c["text2"],
                "flex": 1
            })
        
        if self.supports_reveal:
            footer_buttons.append({
                "type": "button",
                "action": {"type": "message", "label": "إظهار", "text": "جاوب"},
                "style": "secondary",
                "height": "sm",
                "color": c["text2"],
                "flex": 1
            })
        
        footer_buttons.append({
            "type": "button",
            "action": {"type": "message", "label": "إيقاف", "text": "ايقاف"},
            "style": "secondary",
            "height": "sm",
            "color": c["error"],
            "flex": 1
        })
        
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
                "layout": "horizontal",
                "contents": footer_buttons,
                "spacing": "sm",
                "paddingAll": "12px",
                "backgroundColor": c["card"]
            }
        }
        
        return FlexMessage(alt_text=self.game_name, contents=FlexContainer.from_dict(bubble))
    
    def build_text_message(self, text):
        return TextMessage(text=text)
    
    def handle_withdrawal(self, user_id, display_name):
        if user_id in self.withdrawn_users:
            return None
        
        self.withdrawn_users.add(user_id)
        if user_id in self.scores:
            del self.scores[user_id]
        
        return {
            "response": self.build_text_message(f"{display_name} انسحب من اللعبة"),
            "points": 0,
            "withdrawn": True
        }
    
    def start_game(self):
        self.game_active = True
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        self.withdrawn_users = set()
        self.start_time = time.time()
        self.round_start_time = time.time()
        return self.get_question()
    
    @abstractmethod
    def get_question(self):
        pass
    
    @abstractmethod
    def check_answer(self, user_answer, user_id, display_name):
        pass
    
    def end_game(self):
        self.game_active = False
        c = self.get_theme_colors()
        
        if not self.scores:
            bubble = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "انتهت اللعبة", 
                         "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
                        {"type": "separator", "margin": "lg", "color": c["border"]},
                        {"type": "text", "text": "لم يسجل أحد نقاطاً", 
                         "size": "md", "color": c["text2"], "align": "center", "margin": "lg"}
                    ],
                    "paddingAll": "20px",
                    "backgroundColor": c["bg"]
                }
            }
            
            return {
                "game_over": True,
                "points": 0,
                "response": FlexMessage(alt_text="انتهت اللعبة", 
                                       contents=FlexContainer.from_dict(bubble))
            }
        
        sorted_players = sorted(
            self.scores.items(),
            key=lambda x: (-x[1]['score'], x[1].get('correct', 0))
        )
        
        winner = sorted_players[0][1]
        
        leaderboard = [
            {"type": "text", "text": "نتائج اللعبة", 
             "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "الفائز", 
                     "size": "sm", "color": c["success"], "align": "center"},
                    {"type": "text", "text": winner['name'], 
                     "size": "xxl", "weight": "bold", "color": c["text"], 
                     "align": "center", "margin": "sm"},
                    {"type": "text", "text": f"{winner['score']} نقطة", 
                     "size": "lg", "color": c["primary"], "align": "center", "margin": "xs"}
                ],
                "backgroundColor": c["card"],
                "cornerRadius": "12px",
                "paddingAll": "16px",
                "margin": "md"
            }
        ]
        
        if len(sorted_players) > 1:
            leaderboard.extend([
                {"type": "separator", "margin": "lg", "color": c["border"]},
                {"type": "text", "text": "الترتيب النهائي", 
                 "size": "md", "weight": "bold", "color": c["text"], 
                 "align": "center", "margin": "md"}
            ])
            
            for i, (uid, player) in enumerate(sorted_players[:5]):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
                leaderboard.append({
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": medal, 
                         "size": "sm", "flex": 0, "weight": "bold"},
                        {"type": "text", "text": player['name'], 
                         "size": "sm", "color": c["text"], "flex": 3, "margin": "sm"},
                        {"type": "text", "text": str(player['score']), 
                         "size": "sm", "color": c["primary"], "align": "end", 
                         "flex": 1, "weight": "bold"}
                    ],
                    "paddingAll": "8px",
                    "margin": "sm"
                })
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": leaderboard,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "العب مرة أخرى", "text": self.game_name},
                        "style": "primary",
                        "height": "sm",
                        "color": c["primary"],
                        "flex": 1
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "القائمة", "text": "بداية"},
                        "style": "secondary",
                        "height": "sm",
                        "color": c["text2"],
                        "flex": 1
                    }
                ],
                "spacing": "sm",
                "paddingAll": "12px",
                "backgroundColor": c["card"]
            }
        }
        
        return {
            "game_over": True,
            "points": winner['score'],
            "won": True,
            "winner": winner['name'],
            "response": FlexMessage(alt_text="نتائج اللعبة", 
                                   contents=FlexContainer.from_dict(bubble))
        }
