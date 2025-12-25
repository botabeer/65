import random
from games.base_game import BaseGame

class CategoryGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "فئه"

        self.challenges = [
            {"category": "المطبخ", "letter": "ق", "answers": ["قدر", "قلاية"]},
            {"category": "حيوان", "letter": "ب", "answers": ["بطة", "بقرة"]},
            {"category": "فاكهة", "letter": "ت", "answers": ["تفاح", "توت"]},
            {"category": "بلاد", "letter": "س", "answers": ["سعودية", "سوريا"]},
            {"category": "اسم ولد", "letter": "م", "answers": ["محمد", "مصطفى"]},
            {"category": "اسم بنت", "letter": "ف", "answers": ["فاطمة", "فرح"]},
            {"category": "نبات", "letter": "ز", "answers": ["زيتون", "زهرة"]},
            {"category": "جماد", "letter": "ك", "answers": ["كرسي", "كتاب"]},
            {"category": "مهنة", "letter": "ط", "answers": ["طبيب", "طباخ"]},
            {"category": "لون", "letter": "ا", "answers": ["احمر", "ازرق"]},
            {"category": "رياضة", "letter": "ك", "answers": ["كرة", "كاراتيه"]},
            {"category": "مدينة", "letter": "ج", "answers": ["جدة", "جازان"]},
            {"category": "طعام", "letter": "ر", "answers": ["رز", "رمان"]},
            {"category": "شراب", "letter": "ق", "answers": ["قهوة", "قمر الدين"]},
            {"category": "اثاث", "letter": "س", "answers": ["سرير", "سجادة"]},
            {"category": "ملابس", "letter": "ث", "answers": ["ثوب", "ثياب"]},
            {"category": "حشرة", "letter": "ن", "answers": ["نملة", "نحلة"]},
            {"category": "طائر", "letter": "ح", "answers": ["حمامة", "حسون"]},
            {"category": "زهرة", "letter": "و", "answers": ["ورد", "ورقة"]},
            {"category": "معدن", "letter": "ذ", "answers": ["ذهب", "ذرة"]},
            {"category": "الة موسيقية", "letter": "ع", "answers": ["عود", "عصا"]},
            {"category": "سيارة", "letter": "م", "answers": ["مرسيدس", "مازدا"]},
            {"category": "عضو جسم", "letter": "ي", "answers": ["يد", "ياقة"]},
            {"category": "دولة", "letter": "ل", "answers": ["لبنان", "ليبيا"]},
            {"category": "حلوى", "letter": "ب", "answers": ["بسبوسة", "بقلاوة"]},
            {"category": "ادوات مدرسية", "letter": "د", "answers": ["دفتر", "دبوس"]},
            {"category": "وسيلة مواصلات", "letter": "ح", "answers": ["حافلة", "حمار"]},
            {"category": "فصل", "letter": "ش", "answers": ["شتاء", "شروق"]},
            {"category": "شهر", "letter": "ر", "answers": ["رمضان", "رجب"]},
            {"category": "يوم", "letter": "ج", "answers": ["جمعة", "جمعتين"]},
            {"category": "كوكب", "letter": "ز", "answers": ["زهرة", "زحل"]},
            {"category": "بحر", "letter": "ا", "answers": ["احمر", "اسود"]},
            {"category": "جبل", "letter": "ط", "answers": ["طويق", "طور"]},
            {"category": "نهر", "letter": "ن", "answers": ["نيل", "نهر"]},
            {"category": "عاصمة", "letter": "ب", "answers": ["بغداد", "بيروت"]},
            {"category": "قارة", "letter": "ا", "answers": ["اسيا", "افريقيا"]},
            {"category": "محيط", "letter": "ه", "answers": ["هادي", "هندي"]},
            {"category": "صحراء", "letter": "ك", "answers": ["كبرى", "كويت"]},
            {"category": "جزيرة", "letter": "ق", "answers": ["قبرص", "قطر"]},
            {"category": "واد", "letter": "و", "answers": ["وادي", "وادج"]},
            {"category": "دواء", "letter": "ا", "answers": ["اسبرين", "انسولين"]},
            {"category": "مرض", "letter": "س", "answers": ["سكري", "سعال"]},
            {"category": "جهاز طبي", "letter": "م", "answers": ["منظار", "مشرط"]},
            {"category": "جهاز منزلي", "letter": "غ", "answers": ["غسالة", "غلاية"]},
            {"category": "عطر", "letter": "ع", "answers": ["عود", "عنبر"]},
            {"category": "حجر كريم", "letter": "ي", "answers": ["ياقوت", "يشب"]},
            {"category": "معجنات", "letter": "ف", "answers": ["فطيرة", "فتة"]},
            {"category": "مشروب ساخن", "letter": "ش", "answers": ["شاي", "شوكولاتة"]},
            {"category": "حلوى شعبية", "letter": "ك", "answers": ["كنافة", "كعك"]}
        ]

        self.questions = []
        self.first_correct_answer = False

    def start_game(self):
        self.questions = random.sample(
            self.challenges,
            min(self.questions_count, len(self.challenges))
        )
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        self.first_correct_answer = False
        self.game_active = True
        return self.get_question()

    def get_question(self):
        challenge = self.questions[self.current_question]
        self.first_correct_answer = False
        self.previous_question = f"{challenge['category']} حرف {challenge['letter']}"

        return self.build_question_message(
            f"الفئة: {challenge['category']}\nالحرف: {challenge['letter']}"
        )

    def check_answer(self, user_answer, user_id, display_name):
        if self.first_correct_answer or user_id in self.answered_users:
            return None

        challenge = self.questions[self.current_question]
        normalized = self.normalize_text(user_answer)

        if normalized in ["انسحب", "انسحاب"]:
            return self.handle_withdrawal(user_id, display_name)

        if self.supports_hint and normalized == "لمح":
            sample = challenge["answers"][0]
            return {
                "response": self.build_text_message(f"يبدا بحرف: {sample[0]}"),
                "points": 0,
            }

        if self.supports_reveal and normalized == "جاوب":
            answers = " - ".join(challenge["answers"])
            self.first_correct_answer = True
            self.previous_answer = answers
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                return self.end_game()

            return {
                "response": self.get_question(),
                "points": 0,
                "next_question": True
            }

        valid_answers = [self.normalize_text(a) for a in challenge["answers"]]

        if normalized in valid_answers:
            self.answered_users.add(user_id)
            points = self.add_score(user_id, display_name, 1)

            self.first_correct_answer = True
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
