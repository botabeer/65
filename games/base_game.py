from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import re
from typing import Dict, Any, List
from abc import ABC, abstractmethod

class BaseGame(ABC):
    """الفئة الأساسية لجميع الألعاب"""
    
    BUTTON_COLOR = "#F8FBFC"
    
    THEMES = {
        "light": {
            "primary": "#1E293B",
            "text": "#334155",
            "text2": "#64748B",
            "text3": "#94A3B8",
            "bg": "#FFFFFF",
            "card": "#F8FAFC",
            "border": "#E2E8F0",
            "button": "#F2F2F7",
            "success": "#0EA5E9",
            "accent": "#3B82F6",
            "warning": "#F59E0B",
            "error": "#EF4444"
        },
        "dark": {
            "primary": "#F1F5F9",
            "text": "#CBD5E1",
            "text2": "#94A3B8",
            "text3": "#64748B",
            "bg": "#0F172A",
            "card": "#1E293B",
            "border": "#334155",
            "button": "#F2F2F7",
            "success": "#38BDF8",
            "accent": "#60A5FA",
            "warning": "#FBBF24",
            "error": "#F87171"
        }
    }

    def __init__(self, line_bot_api, theme="light", game_type="competitive", difficulty=1):
        self.line_bot_api = line_bot_api
        self.theme = theme
        self.game_type = game_type
        self.difficulty = difficulty
        self.game_name = "لعبة"
        self.questions_count = 5
        self.current_question = 0
        self.game_active = False
        self.scores = {}
        self.answered_users = set()
        self.withdrawn_users = set()
        self.current_answer = None
        self.previous_answer = None
        self.previous_question = None
        self.supports_hint = True
        self.supports_reveal = True
        self.used_questions = set()

    def normalize_text(self, text):
        if not text:
            return ""
        
        text = str(text).strip().lower()
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        
        replacements = {
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا',
            'ى': 'ي', 'ة': 'ه', 'ؤ': 'و', 'ئ': 'ي'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def add_score(self, user_id, display_name, points=1):
        if user_id not in self.scores:
            self.scores[user_id] = {
                'name': display_name,
                'score': 0
            }
        self.scores[user_id]['score'] += points
        return self.scores[user_id]['score']

    def get_theme_colors(self):
        colors = self.THEMES.get(self.theme, self.THEMES['light']).copy()
        defaults = {
            "warning": colors.get("accent", "#F59E0B"),
            "error": colors.get("primary", "#EF4444")
        }
        for key, value in defaults.items():
            if key not in colors:
                colors[key] = value
        return colors

    def build_text_message(self, text):
        return TextMessage(text=text)

    def build_question_message(self, question_text, subtitle=""):
        colors = self.get_theme_colors()
        progress = int((self.current_question / self.questions_count) * 100)

        contents = [
            {
                "type": "text",
                "text": self.game_name,
                "size": "xl",
                "weight": "bold",
                "align": "center",
                "color": colors["primary"]
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": f"السؤال {self.current_question + 1} من {self.questions_count}",
                        "size": "xs",
                        "color": colors["text2"],
                        "align": "center"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "width": f"{progress}%",
                                "height": "4px",
                                "backgroundColor": colors["success"],
                                "cornerRadius": "2px"
                            }
                        ],
                        "height": "4px",
                        "backgroundColor": colors["border"],
                        "cornerRadius": "2px"
                    }
                ]
            }
        ]

        # عرض الجواب السابق فقط بدون السؤال السابق
        if self.previous_answer:
            contents.extend([
                {
                    "type": "separator",
                    "margin": "md",
                    "color": colors["border"]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "sm",
                    "backgroundColor": colors["card"],
                    "cornerRadius": "6px",
                    "paddingAll": "8px",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"الجواب السابق: {self.previous_answer}",
                            "size": "xs",
                            "color": colors["success"],
                            "weight": "bold",
                            "wrap": True
                        }
                    ]
                }
            ])

        contents.extend([
            {
                "type": "separator",
                "margin": "lg",
                "color": colors["border"]
            },
            {
                "type": "text",
                "text": question_text,
                "size": "lg",
                "wrap": True,
                "color": colors["text"],
                "align": "center",
                "margin": "lg"
            }
        ])

        if subtitle:
            contents.append({
                "type": "text",
                "text": subtitle,
                "size": "sm",
                "color": colors["text2"],
                "align": "center",
                "margin": "md"
            })

        footer_buttons = []
        if self.supports_hint:
            footer_buttons.append({
                "type": "button",
                "style": "secondary",
                "height": "sm",
                "action": {
                    "type": "message",
                    "label": "لمح",
                    "text": "لمح"
                },
                "color": self.BUTTON_COLOR,
                "flex": 1
            })
        
        if self.supports_reveal:
            footer_buttons.append({
                "type": "button",
                "style": "secondary",
                "height": "sm",
                "action": {
                    "type": "message",
                    "label": "جاوب",
                    "text": "جاوب"
                },
                "color": self.BUTTON_COLOR,
                "flex": 1
            })
        
        footer_buttons.append({
            "type": "button",
            "style": "secondary",
            "height": "sm",
            "action": {
                "type": "message",
                "label": "ايقاف",
                "text": "ايقاف"
            },
            "color": self.BUTTON_COLOR,
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
                "backgroundColor": colors["bg"]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": footer_buttons,
                "spacing": "sm",
                "paddingAll": "12px",
                "backgroundColor": colors["card"]
            }
        }

        return FlexMessage(
            alt_text=self.game_name,
            contents=FlexContainer.from_dict(bubble)
        )

    def start_game(self):
        self.game_active = True
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        self.withdrawn_users = set()
        self.used_questions = set()
        self.previous_answer = None
        self.previous_question = None
        return self.get_question()

    @abstractmethod
    def get_question(self):
        """يجب تنفيذها في كل لعبة - ترجع السؤال التالي"""
        pass

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.withdrawn_users:
            return None

        normalized = self.normalize_text(user_answer)

        if normalized == "ايقاف":
            return self.handle_withdrawal(user_id, display_name)

        if user_id in self.answered_users:
            return None

        if self.supports_hint and normalized == "لمح":
            return self.handle_hint()

        if self.supports_reveal and normalized == "جاوب":
            return self.handle_reveal()

        return self.validate_answer(normalized, user_id, display_name)

    def handle_hint(self):
        if not self.current_answer:
            return None
        
        answer_sample = self.current_answer[0] if isinstance(self.current_answer, list) else str(self.current_answer)
        hint = f"يبدأ بـ: {answer_sample[0]}\nعدد الحروف: {len(answer_sample)}"
        
        return {
            "response": self.build_text_message(hint),
            "points": 0
        }

    def handle_reveal(self):
        if not self.current_answer:
            return None
        
        answer_text = " او ".join(self.current_answer) if isinstance(self.current_answer, list) else str(self.current_answer)
        self.previous_answer = answer_text
        self.current_question += 1
        self.answered_users.clear()
        
        if self.current_question >= self.questions_count:
            return self.end_game()
        
        return {
            "response": self.get_question(),
            "points": 0,
            "next_question": True
        }

    def validate_answer(self, normalized, user_id, display_name):
        correct_answers = self.current_answer if isinstance(self.current_answer, list) else [self.current_answer]
        
        for correct in correct_answers:
            if self.normalize_text(str(correct)) == normalized:
                return self.handle_correct_answer(user_id, display_name)
        
        return None

    def handle_correct_answer(self, user_id, display_name):
        self.answered_users.add(user_id)
        points = self.add_score(user_id, display_name, 1)
        
        answer_text = " او ".join(self.current_answer) if isinstance(self.current_answer, list) else str(self.current_answer)
        self.previous_answer = answer_text
        
        self.current_question += 1
        self.answered_users.clear()
        
        if self.current_question >= self.questions_count:
            result = self.end_game()
            result["points"] = points
            return result
        
        return {
            "response": self.get_question(),
            "points": points,
            "next_question": True
        }

    def handle_withdrawal(self, user_id, display_name):
        self.withdrawn_users.add(user_id)
        
        if user_id in self.scores:
            del self.scores[user_id]
        
        return {
            "response": self.build_text_message(f"{display_name} انسحب من اللعبة"),
            "points": 0,
            "withdrawn": True,
            "game_over": True
        }

    def end_game(self):
        self.game_active = False
        colors = self.get_theme_colors()
        
        if not self.scores:
            return {
                "response": self.build_text_message("انتهت اللعبة بدون نقاط"),
                "points": 0,
                "game_over": True
            }

        sorted_players = sorted(
            self.scores.items(),
            key=lambda x: -x[1]['score']
        )
        winner = sorted_players[0][1]

        contents = [
            {
                "type": "text",
                "text": "انتهت اللعبة",
                "size": "xl",
                "weight": "bold",
                "align": "center",
                "color": colors["primary"]
            },
            {
                "type": "separator",
                "margin": "md",
                "color": colors["border"]
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "contents": [
                    {
                        "type": "text",
                        "text": winner['name'],
                        "size": "lg",
                        "weight": "bold",
                        "color": colors["text"],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": f"{winner['score']} نقطة",
                        "size": "xxl",
                        "weight": "bold",
                        "color": colors["success"],
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": colors["card"],
                "cornerRadius": "12px",
                "paddingAll": "16px"
            }
        ]

        if len(sorted_players) > 1:
            contents.append({
                "type": "text",
                "text": "النتائج",
                "size": "sm",
                "weight": "bold",
                "color": colors["text"],
                "margin": "lg"
            })
            
            for i, (uid, data) in enumerate(sorted_players[:5]):
                contents.append({
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{i+1}",
                            "size": "sm",
                            "color": colors["text2"],
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": data['name'],
                            "size": "sm",
                            "color": colors["text"],
                            "flex": 3,
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": str(data['score']),
                            "size": "sm",
                            "weight": "bold",
                            "color": colors["primary"],
                            "align": "end",
                            "flex": 1
                        }
                    ]
                })

        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": colors["bg"]
            }
        }

        return {
            "response": FlexMessage(
                alt_text="نتيجة اللعبة",
                contents=FlexContainer.from_dict(bubble)
            ),
            "points": winner['score'],
            "game_over": True,
            "won": True
        }
