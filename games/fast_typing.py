import random
import time
from games.base import BaseGame
from config import Config

class FastTypingGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة الكتابة السريعة"
        self.supports_hint = False
        self.time_limit = 10
        self.start_time = None
        self.phrases = [
            "سبحان الله", "الحمد لله", "لا إله إلا الله", "الله أكبر",
            "استغفر الله", "لا حول ولا قوة إلا بالله",
            "بسم الله الرحمن الرحيم", "السلام عليكم",
            "الصبر مفتاح الفرج", "العلم نور",
            "الوقت من ذهب", "الصديق وقت الضيق",
            "القناعة كنز لا يفنى", "الكتاب خير جليس"
        ]
    
    def get_question(self):
        phrase = random.choice(self.phrases)
        self.current_answer = phrase
        self.start_time = time.time()
        
        question = f"اكتب العبارة التالية بسرعة:\n{phrase}\n\nالوقت: {self.time_limit} ثانية"
        
        return self.build_question_flex(question, None)
    
    def check_answer(self, answer: str) -> bool:
        if self.start_time:
            elapsed = time.time() - self.start_time
            if elapsed > self.time_limit:
                return False
        
        normalized_answer = Config.normalize(answer)
        normalized_correct = Config.normalize(self.current_answer)
        return normalized_answer == normalized_correct
