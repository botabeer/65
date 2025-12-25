import random
from games.base_game import BaseGame

class WordColorGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, game_type="competitive", difficulty=difficulty, theme=theme)
        self.game_name = "لون"
        self.supports_hint = True
        self.supports_reveal = True
        
        self.color_names = ["احمر", "ازرق", "اخضر", "اصفر", "برتقالي", "بنفسجي", "وردي", "اسود", "ابيض"]
        self.current_word = None
        self.current_color_name = None
    
    def get_question(self):
        word = random.choice(self.color_names)
        color_name = random.choice([c for c in self.color_names if c != word]) if random.random() < 0.7 else word
        
        self.current_word = word
        self.current_color_name = color_name
        self.current_answer = [color_name]
        self.previous_question = f"كلمة {word} ملونة بلون {color_name}"
        
        message = f"ما لون هذه الكلمة:\n\n{word}\n\n(تخيل انها مكتوبة بلون {color_name})"
        
        return self.build_question_message(message, "اكتب اسم اللون الذي ترى به الكلمة")
    
    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if normalized in ["انسحب", "انسحاب"]:
            return self.handle_withdrawal(user_id, display_name)
        
        if self.supports_hint and normalized == "لمح":
            answer = self.current_answer[0]
            hint = f"يبدأ بحرف: {answer[0]}\nعدد الحروف: {len(answer)}"
            return {"response": self.build_text_message(hint), "points": 0}
        
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
