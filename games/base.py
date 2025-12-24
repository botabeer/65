from abc import ABC, abstractmethod
from config import SYSTEM_SETTINGS, THEMES, normalize_arabic

class BaseGame(ABC):
    QUESTIONS_PER_GAME = SYSTEM_SETTINGS["questions_per_game"]
    
    def __init__(self, db, theme="light"):
        self.db = db
        self.theme = theme
        self.total_q = self.QUESTIONS_PER_GAME
        self.current_q = 0
        self.score = 0
        self.current_answer = None
        self.supports_hint = True
        self.supports_reveal = True
        self.game_name = "لعبة"
        self.hint_text = None
    
    @abstractmethod
    def get_question(self):
        pass
    
    @abstractmethod
    def check_answer(self, answer: str) -> bool:
        pass
    
    def start(self):
        self.current_q = 1
        self.score = 0
        return self.get_question()
    
    def check(self, answer: str):
        correct = self.check_answer(answer)
        if correct:
            self.score += 1
        
        self.current_q += 1
        
        if self.current_q > self.total_q:
            return self.finish()
        else:
            return self.get_question(), correct
    
    def finish(self):
        return None
    
    def get_hint(self):
        if not self.supports_hint or not self.hint_text:
            return None
        return self.build_hint_message()
    
    def reveal_answer(self):
        if not self.supports_reveal or not self.current_answer:
            return None
        return self.build_reveal_message()
    
    def build_question_flex(self, question_text, hint=None):
        c = THEMES[self.theme]
        self.hint_text = hint
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": self.game_name,
                                "size": "xl",
                                "weight": "bold",
                                "color": c["primary"]
                            },
                            {
                                "type": "text",
                                "text": f"{self.current_q}/{self.total_q}",
                                "size": "sm",
                                "color": c["text_secondary"],
                                "align": "end"
                            }
                        ],
                        "spacing": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": c["border"]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": question_text,
                                "size": "lg",
                                "wrap": True,
                                "color": c["text"]
                            }
                        ],
                        "margin": "lg",
                        "paddingAll": "15px",
                        "backgroundColor": c["hover"],
                        "cornerRadius": "8px"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"النقاط: {self.score}",
                                "size": "sm",
                                "color": c["success"],
                                "weight": "bold"
                            }
                        ],
                        "margin": "md"
                    }
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [],
                        "spacing": "sm"
                    }
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "15px"
            }
        }
        
        buttons = []
        if self.supports_hint and hint:
            buttons.append({
                "type": "button",
                "action": {"type": "message", "label": "تلميح", "text": "لمح"},
                "style": "secondary",
                "color": c["info"],
                "height": "sm"
            })
        
        if self.supports_reveal:
            buttons.append({
                "type": "button",
                "action": {"type": "message", "label": "الإجابة", "text": "جاوب"},
                "style": "secondary",
                "color": c["warning"],
                "height": "sm"
            })
        
        buttons.append({
            "type": "button",
            "action": {"type": "message", "label": "إيقاف", "text": "ايقاف"},
            "style": "secondary",
            "color": c["danger"],
            "height": "sm"
        })
        
        bubble["footer"]["contents"][0]["contents"] = buttons
        
        return {"type": "flex", "altText": question_text, "contents": bubble}
    
    def build_hint_message(self):
        c = THEMES[self.theme]
        return {
            "type": "flex",
            "altText": "تلميح",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "تلميح",
                            "size": "lg",
                            "weight": "bold",
                            "color": c["info"]
                        },
                        {
                            "type": "text",
                            "text": self.hint_text,
                            "size": "md",
                            "wrap": True,
                            "color": c["text"],
                            "margin": "md"
                        }
                    ],
                    "backgroundColor": c["bg"],
                    "paddingAll": "15px"
                }
            }
        }
    
    def build_reveal_message(self):
        c = THEMES[self.theme]
        return {
            "type": "flex",
            "altText": "الإجابة",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "الإجابة الصحيحة",
                            "size": "lg",
                            "weight": "bold",
                            "color": c["warning"]
                        },
                        {
                            "type": "text",
                            "text": str(self.current_answer),
                            "size": "xl",
                            "wrap": True,
                            "color": c["text"],
                            "weight": "bold",
                            "margin": "md"
                        }
                    ],
                    "backgroundColor": c["bg"],
                    "paddingAll": "15px"
                }
            }
        }
