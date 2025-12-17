import random
from games.base import BaseGame
from config import Config

class ScrambleGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة ترتيب الحروف"
        self.words = {
            1: ["كتاب", "قلم", "باب", "حقيبه", "مدرسه"],
            2: ["سياره", "مطبخ", "تلفاز", "حاسوب", "تفاحه"],
            3: ["مستشفى", "جامعه", "مكتبه", "هاتف", "صحيفه"],
            4: ["طائره", "سفينه", "مطعم", "مستودع", "اسطوانه"],
            5: ["مصباح", "منديل", "محفظه", "ثلاجه", "مفتاح"]
        }
    
    def get_question(self):
        level = min(5, (self.current_q + 4) // 5 + 1)
        word = random.choice(self.words[level])
        self.current_answer = word
        
        scrambled = list(word)
        random.shuffle(scrambled)
        while ''.join(scrambled) == word:
            random.shuffle(scrambled)
        
        scrambled_word = ' '.join(scrambled)
        question = f"رتب الحروف:\n{scrambled_word}"
        hint = f"{len(word)} أحرف"
        
        return self.build_question_flex(question, hint)
    
    def check_answer(self, answer: str) -> bool:
        normalized = Config.normalize(answer)
        return normalized == Config.normalize(self.current_answer)
