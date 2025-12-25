import random
from games.base_game import BaseGame

class LetterGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "حروف"
        self.supports_hint = True
        self.supports_reveal = True

        self.all_letters = {
            'ا': ['ادم', 'اثينا', 'الجزائر', 'اسد', 'ارنب', 'ابيض'],
            'ب': ['بغداد', 'بكين', 'بقرة', 'باب', 'بطيخ'],
            'ت': ['تونس', 'تمساح', 'تفاح', 'تمر'],
            'ث': ['ثعلب', 'ثوم', 'ثلج'],
            'ج': ['جيبوتي', 'جمل', 'جزر', 'جبل'],
            'ح': ['حلب', 'حوت', 'حصان', 'حديقة'],
            'خ': ['خرطوم', 'خنساء', 'خروف', 'خيار'],
            'د': ['دبلن', 'دب', 'دجاج', 'دفتر'],
            'ر': ['روما', 'راكون', 'رمان', 'رز'],
            'ز': ['زغرب', 'زرافة', 'زيتون'],
            'س': ['سلحفاة', 'سنجاب', 'سيارة', 'سمك'],
            'ش': ['شارقة', 'شمبانزي', 'شمس', 'شجرة'],
            'ص': ['صنعاء', 'صقر', 'صحن', 'صابون'],
            'ط': ['طهران', 'طاووس', 'طائرة', 'طماطم'],
            'ع': ['عسل', 'عين', 'عنب', 'عصفور'],
            'ف': ['فنلندا', 'فيل', 'فراولة', 'فرن'],
            'ق': ['قطر', 'قنفذ', 'قلم', 'قمر'],
            'ك': ['كتاب', 'كرسي', 'كلب', 'كوب'],
            'ل': ['لبنان', 'ليمون', 'لحاف', 'لوز'],
            'م': ['مخ', 'مانجو', 'مدرسة', 'ملعقة'],
            'ن': ['نيل', 'نسر', 'نملة', 'نافذة'],
            'ه': ['هند', 'هرة', 'هاتف'],
            'و': ['وردة', 'وسادة', 'ورق'],
            'ي': ['يوم', 'يد', 'ياسمين']
        }

        self.questions = []

    def start_game(self):
        letters = list(self.all_letters.keys())
        selected = random.sample(letters, min(self.questions_count, len(letters)))

        self.questions = [
            {"letter": l, "answers": self.all_letters[l]}
            for l in selected
        ]

        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        self.game_active = True
        return self.get_question()

    def get_question(self):
        q = self.questions[self.current_question]
        self.current_answer = q['answers']
        self.previous_question = f"حرف {q['letter']}"
        
        return self.build_question_message(
            f"الحرف: {q['letter']}",
            "اكتب أي كلمة تبدأ بهذا الحرف"
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        q = self.questions[self.current_question]
        letter = self.normalize_text(q["letter"])
        answer = self.normalize_text(user_answer)

        if answer in ["انسحب", "انسحاب"]:
            return self.handle_withdrawal(user_id, display_name)

        if self.supports_hint and answer == "لمح":
            example = q['answers'][0]
            hint = f"مثال: يبدأ بـ {example[0]}\nعدد الحروف: {len(example)}"
            return {"response": self.build_text_message(hint), "points": 0}

        if self.supports_reveal and answer == "جاوب":
            examples = " - ".join(q['answers'][:3])
            self.previous_answer = examples
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                return self.end_game()
            
            return {
                "response": self.get_question(),
                "points": 0,
                "next_question": True
            }

        if answer.startswith(letter):
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
        
        return None
