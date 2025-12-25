from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import re
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class BaseGame(ABC):
    THEMES = {
        "light": {
            "primary": "#2563EB", "success": "#10B981", "warning": "#F59E0B",
            "error": "#EF4444", "info": "#3B82F6", "text": "#1F2937",
            "text2": "#6B7280", "text3": "#9CA3AF", "bg": "#F9FAFB",
            "card": "#FFFFFF", "border": "#E5E7EB", 
            "progress_bg": "#E5E7EB", "progress_fill": "#2563EB"
        },
        "dark": {
            "primary": "#3B82F6", "success": "#34D399", "warning": "#FBBF24",
            "error": "#F87171", "info": "#60A5FA", "text": "#F9FAFB",
            "text2": "#D1D5DB", "text3": "#9CA3AF", "bg": "#1F2937",
            "card": "#374151", "border": "#4B5563",
            "progress_bg": "#374151", "progress_fill": "#3B82F6"
        }
    }
    
    DIFFICULTY_LEVELS = {
        1: {"name": "سهل جدا", "questions": 3, "time": 30, "hint_penalty": 0},
        2: {"name": "سهل", "questions": 5, "time": 25, "hint_penalty": 0},
        3: {"name": "متوسط", "questions": 5, "time": 20, "hint_penalty": 0},
        4: {"name": "صعب", "questions": 7, "time": 15, "hint_penalty": 1},
        5: {"name": "صعب جدا", "questions": 10, "time": 10, "hint_penalty": 2}
    }
    
    def __init__(self, line_bot_api, difficulty=3, theme="light", game_type="competitive", questions_count=None):
        self.line_bot_api = line_bot_api
        self.difficulty = difficulty
        self.difficulty_config = self.DIFFICULTY_LEVELS.get(difficulty, self.DIFFICULTY_LEVELS[3])
        self.questions_count = questions_count if questions_count else self.difficulty_config["questions"]
        self.round_time = self.difficulty_config["time"]
        self.hint_penalty = self.difficulty_config["hint_penalty"]
        
        self.current_question = 0
        self.game_active = False
        self.game_type = game_type
        self.game_name = "لعبة"
        self.theme = theme
        
        self.scores = {}
        self.answered_users = set()
        self.withdrawn_users = set()
        self.registered_players = set()
        
        self.current_answer = None
        self.previous_question = None
        self.previous_answer = None
        self.start_time = None
        self.round_start_time = None
        
        self.supports_hint = True
        self.supports_reveal = True
        self.supports_difficulty = True
        self.show_progress = game_type == "competitive"
    
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
            self.scores[user_id] = {'name': display_name, 'score': 0, 'correct': 0, 'time': 0}
        self.scores[user_id]['score'] += points
        self.scores[user_id]['correct'] += 1
        if self.round_start_time:
            self.scores[user_id]['time'] += time.time() - self.round_start_time
        return points
    
    def get_theme_colors(self):
        return self.THEMES.get(self.theme, self.THEMES['light'])
    
    def create_progress_bar(self, current, total):
        c = self.get_theme_colors()
        percentage = int((current / total) * 100) if total > 0 else 0
        
        return {
            "type": "box", "layout": "vertical",
            "contents": [
                {
                    "type": "box", "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": f"السؤال {current}/{total}", "size": "xs", "color": c["text2"], "flex": 1},
                        {"type": "text", "text": f"{percentage}%", "size": "xs", "color": c["primary"], "align": "end", "flex": 0}
                    ]
                },
                {
                    "type": "box", "layout": "horizontal",
                    "contents": [
                        {"type": "box", "layout": "vertical", "contents": [], "width": f"{percentage}%", "backgroundColor": c["progress_fill"], "height": "6px", "cornerRadius": "3px"}
                    ],
                    "backgroundColor": c["progress_bg"], "height": "6px", "cornerRadius": "3px", "margin": "sm"
                }
            ],
            "margin": "md"
        }
    
    def build_question_message(self, question_text, subtitle=None, show_timer=False):
        c = self.get_theme_colors()
        contents = [
            {"type": "text", "text": self.game_name, "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"}
        ]
        
        if self.show_progress and self.game_type == "competitive":
            contents.append(self.create_progress_bar(self.current_question + 1, self.questions_count))
        
        if self.difficulty_config and self.supports_difficulty:
            contents.append({
                "type": "text", "text": f"المستوى: {self.difficulty_config['name']}", 
                "size": "xxs", "color": c["text3"], "align": "center", "margin": "sm"
            })
        
        contents.append({"type": "separator", "margin": "md", "color": c["border"]})
        
        if self.previous_answer and self.current_question > 0:
            contents.append({
                "type": "text", "text": f"الاجابة السابقة: {self.previous_answer}",
                "size": "xxs", "color": c["text3"], "align": "center", "margin": "sm", "wrap": True
            })
        
        contents.extend([
            {"type": "text", "text": question_text, "size": "md", "wrap": True, "color": c["text"], "align": "center", "margin": "lg"}
        ])
        
        if subtitle:
            contents.append({
                "type": "text", "text": subtitle, "size": "xs", "color": c["text2"], 
                "align": "center", "margin": "sm", "wrap": True
            })
        
        if show_timer and self.round_time:
            contents.append({
                "type": "text", "text": f"الوقت المتاح: {self.round_time} ثانية",
                "size": "xxs", "color": c["warning"], "align": "center", "margin": "sm"
            })
        
        footer_buttons = []
        if self.supports_hint:
            footer_buttons.append({
                "type": "button", "action": {"type": "message", "label": "تلميح", "text": "لمح"},
                "style": "secondary", "height": "sm", "color": c["info"]
            })
        if self.supports_reveal:
            footer_buttons.append({
                "type": "button", "action": {"type": "message", "label": "اظهار الاجابة", "text": "جاوب"},
                "style": "secondary", "height": "sm", "color": c["warning"]
            })
        
        footer_buttons.append({
            "type": "button", "action": {"type": "message", "label": "انسحب", "text": "انسحب"},
            "style": "secondary", "height": "sm", "color": c["error"]
        })
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical", "contents": contents,
                "paddingAll": "20px", "backgroundColor": c["bg"]
            }
        }
        
        if footer_buttons:
            bubble["footer"] = {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "box", "layout": "horizontal", "contents": footer_buttons, "spacing": "sm"}
                ],
                "paddingAll": "12px", "backgroundColor": c["card"]
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
            return {
                "game_over": True,
                "points": 0,
                "message": "انتهت اللعبة - لم يسجل احد نقاطا",
                "response": self.build_text_message("انتهت اللعبة")
            }
        
        sorted_players = sorted(
            self.scores.items(),
            key=lambda x: (-x[1]['score'], x[1].get('time', 999999))
        )
        
        winner = sorted_players[0][1]
        
        leaderboard_contents = [
            {"type": "text", "text": "نتائج اللعبة", "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "الفائز", "size": "md", "weight": "bold", "color": c["success"], "align": "center"},
                    {"type": "text", "text": winner['name'], "size": "xl", "weight": "bold", "color": c["text"], "align": "center", "margin": "sm"},
                    {"type": "text", "text": f"{winner['score']} نقطة", "size": "lg", "color": c["primary"], "align": "center", "margin": "xs"}
                ],
                "backgroundColor": c["card"], "cornerRadius": "12px", "paddingAll": "16px", "margin": "md"
            }
        ]
        
        if len(sorted_players) > 1:
            leaderboard_contents.extend([
                {"type": "separator", "margin": "lg", "color": c["border"]},
                {"type": "text", "text": "الترتيب النهائي", "size": "sm", "weight": "bold", "color": c["text"], "align": "center", "margin": "md"}
            ])
            
            rank_colors = {0: "#FFD700", 1: "#C0C0C0", 2: "#CD7F32"}
            for i, (uid, player) in enumerate(sorted_players[:5]):
                rank_color = rank_colors.get(i, c["text2"])
                leaderboard_contents.append({
                    "type": "box", "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": str(i + 1), "size": "sm", "color": rank_color, "flex": 0, "weight": "bold"},
                        {"type": "text", "text": player['name'], "size": "sm", "color": c["text"], "flex": 3, "margin": "sm"},
                        {"type": "text", "text": str(player['score']), "size": "sm", "color": c["primary"], "align": "end", "flex": 1, "weight": "bold"}
                    ],
                    "margin": "sm", "paddingAll": "8px"
                })
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical", "contents": leaderboard_contents,
                "paddingAll": "20px", "backgroundColor": c["bg"]
            }
        }
        
        return {
            "game_over": True,
            "points": winner['score'],
            "won": True,
            "winner": winner['name'],
            "response": FlexMessage(alt_text="نتائج اللعبة", contents=FlexContainer.from_dict(bubble))
        }
