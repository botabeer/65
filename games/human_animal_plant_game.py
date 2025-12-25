from games.base_game import BaseGame
import random

class HumanAnimalGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "لعبه"
        
        self.letters = list("ابتجحدرزسشصطعفقكلمنهوي")
        random.shuffle(self.letters)
        self.categories = ["إنسان", "حيوان", "نبات", "جماد", "بلاد"]
        
        self.database = {
            "إنسان": {
                "م": ["محمد", "مريم", "مصطفى"], "أ": ["أحمد", "أمل", "أمير"],
                "ع": ["علي", "عمر", "عائشة"], "ف": ["فاطمة", "فهد", "فيصل"],
                "س": ["سارة", "سعيد", "سلمان"], "ر": ["رامي", "رنا", "رشيد"],
                "ح": ["حسن", "حنان", "حمد"], "خ": ["خالد", "خديجة", "خليل"],
                "د": ["داود", "دانة", "دلال"], "ز": ["زيد", "زينب", "زكريا"],
                "ص": ["صالح", "صفية", "صبري"], "ط": ["طارق", "طيبة", "طلال"],
                "ق": ["قاسم", "قمر", "قيس"], "ك": ["كريم", "كوثر", "كمال"],
                "ل": ["لؤي", "لينا", "ليث"], "ن": ["نايف", "نورة", "نبيل"],
                "ه": ["هاني", "هند", "هشام"], "و": ["وليد", "وفاء", "وائل"],
                "ي": ["ياسر", "ياسمين", "يوسف"], "ب": ["باسم", "بدور", "بندر"],
                "ت": ["تركي", "تماضر", "تميم"], "ج": ["جاسم", "جواهر", "جهاد"]
            },
            "حيوان": {
                "أ": ["أسد", "أرنب"], "ج": ["جمل", "جاموس"],
                "ح": ["حصان", "حمار"], "خ": ["خروف"],
                "د": ["دجاجة", "ديك"], "ف": ["فيل", "فهد"],
                "ق": ["قرد", "قطة"], "ن": ["نمر", "نعامة"],
                "ب": ["بقرة", "بطة"], "ث": ["ثعلب", "ثور"],
                "ذ": ["ذئب", "ذبابة"], "ز": ["زرافة", "زواحف"],
                "س": ["سمك", "سلحفاة"], "ش": ["شمبانزي", "شاهين"],
                "ض": ["ضفدع", "ضبع"], "ط": ["طاووس", "طائر"],
                "غ": ["غراب", "غزال"], "ك": ["كلب", "كنغر"],
                "م": ["ماعز", "مها"], "و": ["وعل", "ورل"],
                "ي": ["يمامة", "يعسوب"]
            },
            "نبات": {
                "ت": ["تفاح", "تمر"], "ب": ["بطيخ", "برتقال"],
                "ر": ["رمان"], "ع": ["عنب"],
                "ف": ["فراولة"], "م": ["موز", "مشمش"],
                "ن": ["نخل", "نعناع"], "ز": ["زيتون", "زنجبيل"],
                "خ": ["خيار", "خس"], "ج": ["جزر", "جوافة"],
                "ل": ["ليمون", "لوز"], "ش": ["شمام", "شعير"],
                "ق": ["قمح", "قرنفل"], "ك": ["كوسا", "كزبرة"],
                "ب": ["باذنجان", "بصل"], "ط": ["طماطم", "طرخون"],
                "ح": ["حمص", "حلبة"], "س": ["سبانخ", "سفرجل"]
            },
            "جماد": {
                "ب": ["باب", "بيت"], "ت": ["تلفاز", "تلفون"],
                "س": ["سيارة", "ساعة"], "ق": ["قلم", "قفل"],
                "ك": ["كرسي", "كتاب"], "م": ["مفتاح", "مكتب"],
                "ن": ["نافذة", "نظارة"], "ط": ["طاولة", "طائرة"],
                "ح": ["حاسوب", "حذاء"], "ص": ["صحن", "صابون"],
                "ف": ["فرن", "فنجان"], "ل": ["لحاف", "لوحة"],
                "ش": ["شباك", "شماعة"], "خ": ["خزانة", "خاتم"],
                "ج": ["جدار", "جوال"], "ر": ["راديو", "رف"],
                "د": ["دفتر", "دولاب"], "غ": ["غسالة", "غطاء"]
            },
            "بلاد": {
                "أ": ["أمريكا", "ألمانيا"], "ب": ["بريطانيا", "البرازيل"],
                "ت": ["تركيا", "تونس"], "س": ["السعودية", "سوريا"],
                "ع": ["عمان", "العراق"], "ف": ["فرنسا", "فلسطين"],
                "م": ["مصر", "المغرب"], "ي": ["اليمن", "اليابان"],
                "ل": ["لبنان", "ليبيا"], "ك": ["الكويت", "كندا"],
                "ج": ["الجزائر", "جيبوتي"], "ق": ["قطر", "قبرص"],
                "ا": ["الاردن", "الامارات"], "ص": ["الصين", "الصومال"],
                "ر": ["روسيا", "رومانيا"], "ن": ["النرويج", "نيوزيلندا"],
                "ه": ["الهند", "هولندا"], "ش": ["الشام", "شيلي"]
            }
        }
        
        self.current_category = None
        self.current_letter = None
    
    def get_question(self):
        self.current_letter = self.letters[self.current_question % len(self.letters)]
        self.current_category = random.choice(self.categories)
        self.previous_question = f"{self.current_category} حرف {self.current_letter}"
        
        return self.build_question_message(
            f"الفئة: {self.current_category}\nالحرف: {self.current_letter}"
        )
    
    def get_suggested_answer(self):
        if self.current_category in self.database:
            if self.current_letter in self.database[self.current_category]:
                answers = self.database[self.current_category][self.current_letter]
                if answers:
                    return random.choice(answers)
        return None
    
    def validate_answer(self, normalized_answer):
        if not normalized_answer or len(normalized_answer) < 2:
            return False
        
        required_letter = self.normalize_text(self.current_letter)
        if normalized_answer[0] != required_letter:
            return False
        
        return True
    
    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if normalized in ["ايقاف", "ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)
        
        if self.supports_hint and normalized == "لمح":
            suggested = self.get_suggested_answer()
            hint = f"تبدأ بـ: {suggested[0]}\nعدد الحروف: {len(suggested)}" if suggested else "فكر جيدا"
            return {"response": self.build_text_message(hint), "points": 0}
        
        if self.supports_reveal and normalized == "جاوب":
            suggested = self.get_suggested_answer()
            self.previous_answer = suggested or "متعددة"
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                return self.end_game()
            
            return {
                "response": self.get_question(),
                "points": 0,
                "next_question": True
            }
        
        is_valid = self.validate_answer(normalized)
        
        if not is_valid:
            return None
        
        self.answered_users.add(user_id)
        points = self.add_score(user_id, display_name, 1)
        
        self.previous_answer = user_answer.strip()
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
