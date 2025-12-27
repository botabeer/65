import random
from games.base_game import BaseGame
from linebot.v3.messaging import FlexMessage, FlexContainer

class WordColorGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, game_type="competitive", difficulty=difficulty, theme=theme)
        self.game_name = "لون"
        self.supports_hint = False
        self.supports_reveal = True
        
        self.colors = {
            "احمر": "#DC2626",
            "ازرق": "#2563EB",
            "اخضر": "#16A34A",
            "اصفر": "#CA8A04",
            "برتقالي": "#EA580C",
            "بنفسجي": "#7C3AED",
            "وردي": "#DB2777",
            "بني": "#92400E"
        }
        
        self.color_names = list(self.colors.keys())
        self.used_combinations = []
    
    def get_question(self):
        available = []
        for word in self.color_names:
            for color in self.color_names:
                combo = (word, color)
                if combo not in self.used_combinations:
                    available.append(combo)
        
        if not available:
            self.used_combinations = []
            available = [(w, c) for w in self.color_names for c in self.color_names]
        
        if random.random() < 0.7:
            different_combos = [(w, c) for w, c in available if w != c]
            if different_combos:
                word, color_name = random.choice(different_combos)
            else:
                word, color_name = random.choice(available)
        else:
            same_combos = [(w, c) for w, c in available if w == c]
            if same_combos:
                word, color_name = random.choice(same_combos)
            else:
                word, color_name = random.choice(available)
        
        self.used_combinations.append((word, color_name))
        self.current_answer = [color_name]
        self.current_word = word
        self.previous_question = f"كلمة {word} بلون {color_name}"
        
        c = self.get_theme_colors()
        hex_color = self.colors[color_name]
        
        progress = int((self.current_question / self.questions_count) * 100)
        
        contents = [
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "flex": 1,
                        "contents": [
                            {
                                "type": "text", 
                                "text": self.game_name, 
                                "weight": "bold", 
                                "size": "lg", 
                                "color": c["text"]
                            },
                            {
                                "type": "text", 
                                "text": f"السؤال {self.current_question + 1}/{self.questions_count}", 
                                "size": "xs", 
                                "color": c["text2"], 
                                "margin": "xs"
                            }
                        ]
                    }
                ]
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
                        "backgroundColor": c["success"],
                        "cornerRadius": "2px"
                    }
                ],
                "height": "4px",
                "backgroundColor": c["border"],
                "cornerRadius": "2px"
            },
            {
                "type": "separator", 
                "margin": "lg", 
                "color": c["border"]
            },
            {
                "type": "text",
                "text": "ما لون هذه الكلمة",
                "size": "sm",
                "color": c["text2"],
                "align": "center",
                "margin": "lg"
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "backgroundColor": c["card"],
                "cornerRadius": "12px",
                "paddingAll": "20px",
                "borderWidth": "2px",
                "borderColor": hex_color,
                "contents": [
                    {
                        "type": "text",
                        "text": word,
                        "size": "xxl",
                        "weight": "bold",
                        "color": hex_color,
                        "align": "center"
                    }
                ]
            },
            {
                "type": "text",
                "text": "اكتب اسم اللون الذي ترى به الكلمة",
                "size": "xs",
                "color": c["text3"],
                "align": "center",
                "wrap": True,
                "margin": "md"
            }
        ]
        
        footer_buttons = []
        
        if self.supports_reveal:
            footer_buttons.append({
                "type": "button",
                "action": {
                    "type": "message", 
                    "label": "جاوب", 
                    "text": "جاوب"
                },
                "style": "secondary",
                "color": self.BUTTON_COLOR,
                "height": "sm",
                "flex": 1
            })
        
        footer_buttons.append({
            "type": "button",
            "action": {
                "type": "message", 
                "label": "ايقاف", 
                "text": "ايقاف"
            },
            "style": "secondary",
            "color": self.BUTTON_COLOR,
            "height": "sm",
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
        
        return FlexMessage(
            alt_text=self.game_name, 
            contents=FlexContainer.from_dict(bubble)
        )
    
    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if normalized in ["ايقاف", "ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)
        
        if self.supports_reveal and normalized == "جاوب":
            self.previous_answer = self.current_answer[0]
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                return self.end_game()
            
            return {
                "response": self.get_question(),
                "points": 0,
                "next_question": True
            }
        
        correct = self.normalize_text(self.current_answer[0])
        
        if normalized == correct:
            self.answered_users.add(user_id)
            points = self.add_score(user_id, display_name, 1)
            self.previous_answer = self.current_answer[0]
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
        
        return None
