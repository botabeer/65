from linebot.v3.messaging import TextMessage
import random
from .base_game import BaseGame

class LetterGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, game_type="competitive", difficulty=difficulty, theme=theme)
        self.game_name = "حروف"
        
        self.all_letters = {
            'ا': ['ادم', 'اثينا', 'الجزائر', 'اسمرة', 'ابوبكر', 'اسيا', 'اسد'],
            'ب': ['بغداد', 'بكين', 'بيروت', 'برلين', 'باريس', 'بقرة', 'ببغاء'],
            'ت': ['تونس', 'تايبيه', 'تبليسي', 'تيرانا', 'تالين', 'تمساح'],
            'ث': ['ثعلب', 'ثوم', 'ثعبان', 'ثريد', 'ثور'],
            'ج': ['جيبوتي', 'جدة', 'جمل', 'جربوع', 'جراد'],
            'ح': ['حلب', 'حماة', 'حائل', 'حمص', 'حج', 'حوت'],
            'خ': ['خرطوم', 'خبر', 'خميس مشيط', 'خندق', 'خنساء'],
            'د': ['دبلن', 'دمشق', 'دبي', 'دوحة', 'دكار', 'دب'],
            'ذ': ['ذئب', 'ذهب', 'ذرة', 'ذباب', 'ذقن'],
            'ر': ['روما', 'روسيا', 'ريكيافيك', 'رز', 'راكون'],
            'ز': ['زغرب', 'زيمبابوي', 'زنجبار', 'زحل', 'زرافة'],
            'س': ['سلحفاة', 'سنجاب', 'سلطنة عمان', 'سمك', 'ستوكهولم'],
            'ش': ['شرم الشيخ', 'شيتا', 'شارقة', 'شنغهاي', 'شمبانزي'],
            'ص': ['صنعاء', 'صقر', 'صبار', 'صيف', 'صحراء'],
            'ض': ['ضفدع', 'ضابط', 'ضرس العقل', 'ضحى', 'ضبع'],
            'ط': ['طاجيكستان', 'طهر عربي', 'طاجين', 'طاووس', 'طلح'],
            'ظ': ['ظلم', 'ظهر', 'ظبي', 'ظمأ', 'ظفر'],
            'ع': ['عسل', 'عين', 'عمان', 'عقل', 'عنب'],
            'غ': ['غور الاردن', 'غزال', 'غينيا', 'غراب', 'غرناطة'],
            'ف': ['فنلندا', 'فرنسا', 'فيل', 'فهد', 'فارس'],
            'ق': ['قطر', 'قاهرة', 'قسنطينة', 'قنفذ', 'قمح'],
            'ك': ['كوالالمبور', 'كابول', 'كييف', 'كمباال', 'كنغر'],
            'ل': ['ليرة لبنانية', 'ليمون', 'لحاء', 'لوحة', 'ليثيوم'],
            'م': ['مخ', 'مرسيدس', 'معدة', 'ميكروفون', 'مانجو'],
            'ن': ['نيل', 'نسر', 'نمر', 'نور', 'نقود'],
            'ه': ['هوليوود', 'هاني شاكر', 'هيرميس', 'هرم'],
            'و': ['ويندسر', 'وداع للامة', 'ويتني هيوستن', 'ورد'],
            'ي': ['يوم', 'يد', 'يقين', 'يسار', 'يمين']
        }
        
        self.questions = []

    def start_game(self):
        available_letters = list(self.all_letters.keys())
        selected_letters = random.sample(available_letters, min(self.questions_count, len(available_letters)))
        self.questions = [{'letter': letter, 'answers': self.all_letters[letter]} for letter in selected_letters]
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        self.game_active = True
        return self.get_question()

    def get_question(self):
        question = self.questions[self.current_question]
        letter = question['letter']
        self.previous_question = f"الحرف: {letter}"
        
        return self.build_question_message(
            f"الحرف: {letter}\n\nاكتب اي كلمة تبدا بهذا الحرف"
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        question = self.questions[self.current_question]
        letter = question['letter']
        
        normalized = self.normalize_text(user_answer)
        
        if normalized in ["انسحب", "انسحاب"]:
            return self.handle_withdrawal(user_id, display_name)
        
        if self.supports_hint and normalized == "لمح":
            sample = question['answers'][0] if question['answers'] else "كلمة"
            return {'response': self.build_text_message(f"تلميح: {sample}"), 'points': 0}

        if self.supports_reveal and normalized == "جاوب":
            examples = ' - '.join(question['answers'][:3])
            self.previous_answer = examples
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                return self.end_game()
            
            return {
                'response': self.get_question(),
                'points': 0,
                'next_question': True
            }

        if normalized.startswith(self.normalize_text(letter)):
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
                'response': self.get_question(),
                'points': points,
                'next_question': True
            }

        return None
