import random
from games.base_game import BaseGame

class LetterGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "حروف"

        self.all_letters = {
            'ا': ['ادم', 'اثينا', 'الجزائر', 'اسد'],
            'ب': ['بغداد', 'بكين', 'بقرة'],
            'ت': ['تونس', 'تمساح'],
            'ث': ['ثعلب', 'ثوم'],
            'ج': ['جيبوتي', 'جمل'],
            'ح': ['حلب', 'حوت'],
            'خ': ['خرطوم', 'خنساء'],
            'د': ['دبلن', 'دب'],
            'ر': ['روما', 'راكون'],
            'ز': ['زغرب', 'زرافة'],
            'س': ['سلحفاة', 'سنجاب'],
            'ش': ['شارقة', 'شمبانزي'],
            'ص': ['صنعاء', 'صقر'],
            'ط': ['طهران', 'طاووس'],
            'ع': ['عسل', 'عين'],
            'ف': ['فنلندا', 'فيل'],
            'ق': ['قطر', 'قنفذ'],
            'م': ['مخ', 'مانجو'],
            'ن': ['نيل', 'نسر'],
            'ي': ['يوم', 'يد']
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
        return self.build_question_message(
            f"الحرف: {q['letter']}\nاكتب أي كلمة تبدأ بهذا الحرف"
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        q = self.questions[self.current_question]
        letter = self.normalize_text(q["letter"])
        answer = self.normalize_text(user_answer)

        if answer in ["انسحب", "انسحاب"]:
            return self.handle_withdrawal(user_id, display_name)

        if answer.startswith(letter):
            self.answered_users.add(user_id)
            points = self.add_score(user_id, display_name, 1)

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
