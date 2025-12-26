from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import re, time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class BaseGame(ABC):
    THEMES = {
        "light": {
            "primary": "#1A1A1A", "text": "#2D2D2D", "text2": "#6B7280",
            "text3": "#9CA3AF", "bg": "#FFFFFF", "card": "#F9FAFB",
            "border": "#E5E7EB", "button": "#F5F5F5", "success": "#2563EB",
            "warning": "#F59E0B", "error": "#EF4444"
        },
        "dark": {
            "primary": "#F9FAFB", "text": "#E5E7EB", "text2": "#9CA3AF",
            "text3": "#6B7280", "bg": "#111827", "card": "#1F2937",
            "border": "#374151", "button": "#F5F5F5", "success": "#60A5FA",
            "warning": "#FBBF24", "error": "#F87171"
        }
    }
    
    def __init__(self, line_bot_api, theme="light", game_type="competitive"):
        self.line_bot_api = line_bot_api
        self.theme = theme
        self.game_type = game_type
        self.game_name = "لعبة"
        self.questions_count = 5
        self.current_question = 0
        self.game_active = False
        self.scores = {}
        self.answered_users = set()
        self.withdrawn_users = set()
        self.used_questions = set()
        self.current_answer = None
        self.previous_answer = None
        self.previous_question = None
        self.start_time = None
        self.round_start_time = None
        self.supports_hint = True
        self.supports_reveal = True
        self.hints_used = 0
    
    def normalize_text(self, text):
        if not text:
            return ""
        text = str(text).strip().lower()
        trans = str.maketrans({
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا',
            'ؤ': 'و', 'ئ': 'ي', 'ء': '', 'ة': 'ه', 'ى': 'ي'
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
    
    def create_progress_bar(self):
        c = self.get_theme_colors()
        progress = int((self.current_question / self.questions_count) * 100)
        
        return {
            "type": "box", "layout": "vertical",
            "contents": [
                {
                    "type": "box", "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": f"السؤال {self.current_question + 1} من {self.questions_count}", 
                         "size": "xs", "color": c["text2"], "flex": 1},
                    ]
                },
                {
                    "type": "box", "layout": "horizontal",
                    "contents": [{
                        "type": "box", "layout": "vertical", "contents": [],
                        "width": f"{progress}%", "height": "4px",
                        "backgroundColor": c["success"], "cornerRadius": "2px"
                    }],
                    "height": "4px", "backgroundColor": c["border"],
                    "cornerRadius": "2px", "margin": "sm"
                }
            ], "margin": "md"
        }
    
    def build_question_message(self, question_text, subtitle=None, show_timer=False):
        c = self.get_theme_colors()
        
        contents = [
            {"type": "text", "text": self.game_name, "size": "xl", "weight": "bold", 
             "color": c["primary"], "align": "center"},
            self.create_progress_bar(),
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        
        if self.previous_answer and self.current_question > 0:
            contents.append({
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "الإجابة السابقة", 
                     "size": "xs", "color": c["success"], "weight": "bold"},
                    {"type": "text", "text": str(self.previous_answer), 
                     "size": "sm", "color": c["text"], "wrap": True, "margin": "xs"}
                ],
                "backgroundColor": c["card"], "paddingAll": "12px",
                "cornerRadius": "8px", "margin": "md"
            })
        
        contents.append({
            "type": "text", "text": question_text, "size": "lg", 
            "wrap": True, "color": c["text"], "align": "center", "margin": "lg",
            "weight": "bold"
        })
        
        if subtitle:
            contents.append({
                "type": "text", "text": subtitle, "size": "sm", 
                "color": c["text2"], "align": "center", "margin": "sm", "wrap": True
            })
        
        footer_buttons = []
        if self.supports_hint:
            footer_buttons.append({
                "type": "button",
                "action": {"type": "message", "label": "لمح", "text": "لمح"},
                "style": "secondary", "height": "sm",
                "color": c["button"], "flex": 1
            })
        
        if self.supports_reveal:
            footer_buttons.append({
                "type": "button",
                "action": {"type": "message", "label": "جاوب", "text": "جاوب"},
                "style": "secondary", "height": "sm",
                "color": c["button"], "flex": 1
            })
        
        footer_buttons.append({
            "type": "button",
            "action": {"type": "message", "label": "ايقاف", "text": "ايقاف"},
            "style": "secondary", "height": "sm",
            "color": c["button"], "flex": 1
        })
        
        bubble = {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": contents, "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box", "layout": "horizontal",
                "contents": footer_buttons, "spacing": "sm",
                "paddingAll": "12px", "backgroundColor": c["card"]
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
            "points": 0, "withdrawn": True
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
                    "type": "box", "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "انتهت اللعبة", 
                         "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
                        {"type": "separator", "margin": "lg", "color": c["border"]},
                        {"type": "text", "text": "لم يسجل احد نقاطا", 
                         "size": "md", "color": c["text2"], "align": "center", "margin": "lg"}
                    ],
                    "paddingAll": "20px", "backgroundColor": c["bg"]
                }
            }
            return {
                "game_over": True, "points": 0,
                "response": FlexMessage(alt_text="انتهت اللعبة", 
                                       contents=FlexContainer.from_dict(bubble))
            }
        
        sorted_players = sorted(self.scores.items(),
                               key=lambda x: (-x[1]['score'], x[1].get('correct', 0)))
        winner = sorted_players[0][1]
        
        leaderboard = [
            {"type": "text", "text": "نتائج اللعبة", 
             "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "الفائز", 
                     "size": "sm", "color": c["success"], "align": "center", "weight": "bold"},
                    {"type": "text", "text": winner['name'], 
                     "size": "xxl", "weight": "bold", "color": c["text"], 
                     "align": "center", "margin": "sm"},
                    {"type": "text", "text": f"{winner['score']} نقطة", 
                     "size": "lg", "color": c["primary"], "align": "center", "margin": "xs"}
                ],
                "backgroundColor": c["card"], "cornerRadius": "12px",
                "paddingAll": "16px", "margin": "md"
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
                leaderboard.append({
                    "type": "box", "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": f"{i+1}", 
                         "size": "sm", "flex": 0, "weight": "bold", "color": c["primary"]},
                        {"type": "text", "text": player['name'], 
                         "size": "sm", "color": c["text"], "flex": 3, "margin": "sm"},
                        {"type": "text", "text": str(player['score']), 
                         "size": "sm", "color": c["success"], "align": "end", 
                         "flex": 1, "weight": "bold"}
                    ],
                    "paddingAll": "8px", "margin": "sm"
                })
        
        bubble = {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": leaderboard, "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box", "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "لعب مرة اخرى", "text": self.game_name},
                        "style": "secondary", "height": "sm",
                        "color": c["button"], "flex": 1
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "بداية", "text": "بداية"},
                        "style": "secondary", "height": "sm",
                        "color": c["button"], "flex": 1
                    }
                ],
                "spacing": "sm", "paddingAll": "12px",
                "backgroundColor": c["card"]
            }
        }
        
        return {
            "game_over": True, "points": winner['score'],
            "won": True, "winner": winner['name'],
            "response": FlexMessage(alt_text="نتائج اللعبة", 
                                   contents=FlexContainer.from_dict(bubble))
        }
