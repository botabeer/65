import random
from games.base import BaseGame
from config import Config

class HumanAnimalGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة إنسان حيوان"
        self.data = {
            "إنسان": {
                "أ": ["احمد", "أحمد", "علي", "عمر"], "م": ["محمد", "مريم", "منى"],
                "س": ["سارة", "سالم", "سعد"], "ف": ["فاطمة", "فهد"],
                "ن": ["نورة", "نايف"], "خ": ["خالد", "خديجة"]
            },
            "حيوان": {
                "أ": ["اسد", "أسد", "ارنب", "أرنب"], "ق": ["قط", "قرد"],
                "ف": ["فيل", "فار"], "ح": ["حصان", "حمار"],
                "ن": ["نمر", "نعجة"], "ك": ["كلب"]
            },
            "نبات": {
                "و": ["ورد", "ورده"], "ن": ["نخيل", "نعناع"],
                "ر": ["ريحان", "رمان"], "ز": ["زيتون"],
                "ت": ["تفاح", "توت"], "ع": ["عنب"]
            },
            "جماد": {
                "ك": ["كرسي", "كتاب"], "ب": ["باب", "بيت"],
                "ط": ["طاولة", "طاوله"], "س": ["سرير", "سيارة"],
                "ق": ["قلم"], "م": ["مفتاح"]
            },
            "بلاد": {
                "م": ["مصر", "المغرب"], "س": ["السعودية", "سوريا"],
                "ل": ["لبنان", "ليبيا"], "ا": ["الإمارات", "الأردن"],
                "ع": ["العراق", "عمان"], "ق": ["قطر"]
            }
        }
    
    def get_question(self):
        category = random.choice(list(self.data.keys()))
        letter = random.choice(list(self.data[category].keys()))
        self.current_answer = self.data[category][letter]
        
        question = f"الفئة: {category}\nالحرف: {letter}\n\nاكتب كلمة مناسبة"
        hint = f"عدد الإجابات: {len(self.current_answer)}"
        
        return self.build_question_flex(question, hint)
    
    def check_answer(self, answer: str) -> bool:
        normalized = Config.normalize(answer)
        return any(normalized == Config.normalize(ans) for ans in self.current_answer)
