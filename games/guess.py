import random
from games.base import BaseGame
from config import Config

class GuessGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة خمن"
        self.categories = {
            "المطبخ": {
                "أ": ["اناء", "إناء"], "ف": ["فرن"], "م": ["ملعقه", "ملعقة", "مقلاه", "مقلاة"],
                "س": ["سكين", "سكينه"], "ك": ["كوب", "كاسه", "كأس"]
            },
            "غرفة النوم": {
                "س": ["سرير"], "و": ["وساده", "وسادة"], "خ": ["خزانه", "خزانة"],
                "ل": ["لحاف"], "م": ["مرآه", "مرآة", "مخده", "مخدة"]
            },
            "المدرسة": {
                "ق": ["قلم"], "ك": ["كتاب", "كراس", "كراسه"], "م": ["ممحاه", "ممحاة"],
                "ط": ["طاوله", "طاولة"], "س": ["سبوره", "سبورة"]
            },
            "الفواكه": {
                "ت": ["تفاح", "تفاحه"], "م": ["موز"], "ب": ["برتقال"],
                "ع": ["عنب"], "ر": ["رمان"]
            },
            "الحيوانات": {
                "أ": ["اسد", "أسد", "ارنب", "أرنب"], "ق": ["قط", "قطه"], "ك": ["كلب"],
                "ف": ["فيل"], "ح": ["حصان"]
            },
            "المهن": {
                "ط": ["طبيب"], "م": ["معلم", "مهندس"], "ش": ["شرطي"],
                "ن": ["نجار"], "خ": ["خباز"]
            },
            "الألوان": {
                "أ": ["احمر", "أحمر", "ازرق", "أزرق", "اخضر", "أخضر"], "ا": ["اصفر", "أصفر"],
                "ب": ["بني"], "ر": ["رمادي"]
            },
            "الملابس": {
                "ق": ["قميص"], "ب": ["بنطال", "بنطلون"], "ج": ["جاكيت", "جوارب"],
                "ف": ["فستان"], "ح": ["حذاء"]
            },
            "الرياضات": {
                "ك": ["كره", "كرة"], "س": ["سباحه", "سباحة"], "ج": ["جري"],
                "ت": ["تنس"], "ق": ["قفز"]
            },
            "الطيور": {
                "ح": ["حمامه", "حمامة"], "ن": ["نسر"], "ب": ["ببغاء"],
                "د": ["دجاجه", "دجاجة"], "ع": ["عصفور"]
            }
        }
    
    def get_question(self):
        category = random.choice(list(self.categories.keys()))
        letter = random.choice(list(self.categories[category].keys()))
        self.current_answer = self.categories[category][letter]
        
        question = f"الفئة: {category}\nالحرف الأول: {letter}\nما هي؟"
        hint = f"عدد الإجابات المحتملة: {len(self.current_answer)}"
        
        return self.build_question_flex(question, hint)
    
    def check_answer(self, answer: str) -> bool:
        normalized = Config.normalize(answer)
        return any(normalized == Config.normalize(ans) for ans in self.current_answer)
