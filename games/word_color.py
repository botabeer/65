 import random
from games.base import BaseGame
from config import Config

class WordColorGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة الألوان"
        self.supports_hint = False
        self.colors = {
            "احمر": "أحمر",
            "أحمر": "أحمر",
            "ازرق": "أزرق",
            "أزرق": "أزرق",
            "اخضر": "أخضر",
            "أخضر": "أخضر",
            "اصفر": "أصفر",
            "أصفر": "أصفر",
            "برتقالي": "برتقالي",
            "بنفسجي": "بنفسجي",
            "وردي": "وردي",
            "بني": "بني"
        }
    
    def get_question(self):
        word = random.choice(list(self.colors.keys()))
        actual_color = random.choice(list(self.colors.keys()))
        
        if random.random() < 0.7:
            while actual_color == word:
                actual_color = random.choice(list(self.colors.keys()))
        
        self.current_answer = [actual_color, self.colors[actual_color]]
        
        question = f"ما لون هذه الكلمة؟\n\n{self.colors[word]}\n\n(اللون الفعلي للكلمة، ليس معناها)"
        
        return self.build_question_flex(question, None)
    
    def check_answer(self, answer: str) -> bool:
        normalized = Config.normalize(answer)
        return any(normalized == Config.normalize(ans) for ans in self.current_answer)
