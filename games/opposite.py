import random
from games.base import BaseGame
from config import Config

class OppositeGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة الأضداد"
        self.opposites = [
            {"word": "كبير", "opposite": ["صغير", "قصير"]},
            {"word": "طويل", "opposite": ["قصير"]},
            {"word": "سريع", "opposite": ["بطيء", "بطي"]},
            {"word": "ساخن", "opposite": ["بارد"]},
            {"word": "نظيف", "opposite": ["وسخ", "قذر"]},
            {"word": "جميل", "opposite": ["قبيح"]},
            {"word": "غني", "opposite": ["فقير"]},
            {"word": "قوي", "opposite": ["ضعيف"]},
            {"word": "صعب", "opposite": ["سهل"]},
            {"word": "مظلم", "opposite": ["مضيء", "منير"]},
            {"word": "ثقيل", "opposite": ["خفيف"]},
            {"word": "واسع", "opposite": ["ضيق"]},
            {"word": "طري", "opposite": ["قاسي", "صلب"]},
            {"word": "مفتوح", "opposite": ["مغلق"]},
            {"word": "حلو", "opposite": ["مر", "مالح"]},
            {"word": "جاف", "opposite": ["رطب", "مبلول"]},
            {"word": "عالي", "opposite": ["منخفض", "واطي"]},
            {"word": "جديد", "opposite": ["قديم"]},
            {"word": "نشيط", "opposite": ["كسول", "خامل"]},
            {"word": "شجاع", "opposite": ["جبان", "خواف"]},
            {"word": "صادق", "opposite": ["كاذب"]},
            {"word": "محبوب", "opposite": ["مكروه"]},
            {"word": "أمين", "opposite": ["خائن"]},
            {"word": "قريب", "opposite": ["بعيد"]},
            {"word": "حي", "opposite": ["ميت"]},
            {"word": "صحيح", "opposite": ["خطأ", "خاطئ"]},
            {"word": "نعم", "opposite": ["لا"]},
            {"word": "داخل", "opposite": ["خارج"]},
            {"word": "فوق", "opposite": ["تحت"]},
            {"word": "أمام", "opposite": ["خلف", "وراء"]}
        ]
        random.shuffle(self.opposites)
    
    def get_question(self):
        pair = self.opposites[self.current_q - 1]
        self.current_answer = pair["opposite"]
        
        question = f"ما هو عكس كلمة:\n{pair['word']}"
        hint = f"الإجابات المحتملة: {len(pair['opposite'])}"
        
        return self.build_question_flex(question, hint)
    
    def check_answer(self, answer: str) -> bool:
        normalized = Config.normalize(answer)
        return any(normalized == Config.normalize(ans) for ans in self.current_answer)
