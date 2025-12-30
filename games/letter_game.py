import random
from games.base_game import BaseGame


class LetterGame(BaseGame):
    """لعبة الحروف - اسئلة تبدأ بحرف معين"""

    def __init__(self, line_bot_api, difficulty=3, theme="light"):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)

        self.game_name = "حرف"
        self.supports_hint = True
        self.supports_reveal = True

        # بنك الاسئلة
        self.questions_db = {
            "أ": [
                {"q": "من هو اول نبي", "a": ["آدم", "ادم"]},
                {"q": "ما اسم الكوكب الاحمر", "a": ["المريخ"]},
                {"q": "ما هي عاصمة الارجنتين", "a": ["بوينس ايرس"]},
                {"q": "ما اطول نهر في افريقيا", "a": ["النيل"]},
                {"q": "ما الحيوان الذي يعيش في القطب الجنوبي", "a": ["بطريق"]},
            ],
            "ب": [
                {"q": "ما هي عاصمة العراق", "a": ["بغداد"]},
                {"q": "ما هي عاصمة الصين", "a": ["بكين"]},
                {"q": "ما الحيوان الذي يعيش في الماء وله خياشيم", "a": ["سمك"]},
                {"q": "ما اسم اطول سور في العالم", "a": ["سور الصين"]},
                {"q": "ما اسم اكبر قارة في العالم", "a": ["اسيا"]},
            ],
            "ت": [
                {"q": "ما هي عاصمة تونس", "a": ["تونس"]},
                {"q": "ما هي عاصمة تركيا", "a": ["انقرة"]},
                {"q": "ما المادة التي يصنع منها الزجاج", "a": ["رمل"]},
                {"q": "ما الجهاز المستخدم للاتصال", "a": ["هاتف"]},
                {"q": "ما البحر الذي يفصل اوروبا عن افريقيا", "a": ["البحر المتوسط"]},
            ],
            "ج": [
                {"q": "ما هي عاصمة اليابان", "a": ["طوكيو"]},
                {"q": "ما الحيوان ملك الغابة", "a": ["اسد"]},
                {"q": "ما الحيوان المعروف بسفينة الصحراء", "a": ["جمل"]},
                {"q": "ما اسم اكبر محيط في العالم", "a": ["المحيط الهادئ"]},
                {"q": "ما اليوم الاول في الاسبوع", "a": ["الاحد"]},
            ],
            "ح": [
                {"q": "ما المدينة السورية المشهورة بقلعتها", "a": ["حلب"]},
                {"q": "ما الحيوان المعروف ببطئه", "a": ["سلحفاة"]},
                {"q": "ما اسم عاصمة الاردن", "a": ["عمان"]},
                {"q": "ما العضو المسؤول عن ضخ الدم", "a": ["قلب"]},
                {"q": "ما اعلى جبل في العالم", "a": ["ايفرست"]},
            ],
            "س": [
                {"q": "ما هي عاصمة السويد", "a": ["ستوكهولم"]},
                {"q": "ما الحيوان الزاحف ذو الصدفة", "a": ["سلحفاة", "سلحفاه"]},
                {"q": "من الصحابي الذي اشار بحفر الخندق", "a": ["سلمان الفارسي", "سلمان"]},
                {"q": "ما اسم الجهاز الذي يعرض الصور", "a": ["تلفاز"]},
                {"q": "ما اطول نهر في اوروبا", "a": ["الفولغا"]},
            ],
            "م": [
                {"q": "ما العضو المسؤول عن التفكير", "a": ["مخ", "دماغ"]},
                {"q": "ما الشركة التي تصنع سيارات فاخرة", "a": ["مرسيدس"]},
                {"q": "ما المعدن الاصفر الثمين", "a": ["ذهب"]},
                {"q": "ما اسم عاصمة المغرب", "a": ["الرباط"]},
                {"q": "ما اكبر بحر مغلق في العالم", "a": ["بحر قزوين"]},
            ],
            "ن": [
                {"q": "ما اكبر نهر في العالم", "a": ["النيل"]},
                {"q": "ما الطائر رمز الحرية", "a": ["نسر"]},
                {"q": "ما الحيوان رمز القوة", "a": ["نمر"]},
                {"q": "ما اسم الكوكب الذي نعيش عليه", "a": ["الارض"]},
                {"q": "ما اسم عاصمة النرويج", "a": ["اوسلو"]},
            ],
        }

        # تجهيز الحروف
        self.letters = list(self.questions_db.keys())
        random.shuffle(self.letters)

        # تتبع الاسئلة المستخدمة لكل حرف - الحل الصحيح
        self.used_questions = {letter: set() for letter in self.letters}

        self.current_letter = None
        self.current_question_data = None

    def get_question(self):
        if self.current_question >= self.questions_count:
            return self.end_game()

        self.current_letter = self.letters[
            self.current_question % len(self.letters)
        ]

        used = self.used_questions[self.current_letter]
        total = len(self.questions_db[self.current_letter])

        available = [i for i in range(total) if i not in used]

        if not available:
            used.clear()
            available = list(range(total))

        idx = random.choice(available)
        used.add(idx)

        self.current_question_data = self.questions_db[self.current_letter][idx]
        self.current_answer = self.current_question_data["a"]

        question_text = (
            f"حرف: {self.current_letter}\n\n{self.current_question_data['q']}"
        )

        return self.build_question_message(
            question_text,
            f"الاجابة تبدا بحرف {self.current_letter}",
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)

        if normalized == "ايقاف":
            return self.handle_withdrawal(user_id, display_name)

        if self.supports_hint and normalized == "لمح":
            ans = self.current_answer[0]
            hint = f"يبدا بحرف: {ans[0]}\nعدد الحروف: {len(ans)}"
            return {"response": self.build_text_message(hint), "points": 0}

        if self.supports_reveal and normalized == "جاوب":
            self.previous_answer = " او ".join(self.current_answer)
            self.current_question += 1
            self.answered_users.clear()
            return {
                "response": self.get_question(),
                "points": 0,
                "next_question": True,
            }

        for correct in self.current_answer:
            if normalized == self.normalize_text(correct):
                self.answered_users.add(user_id)
                points = self.add_score(user_id, display_name, 1)

                self.previous_answer = correct
                self.current_question += 1
                self.answered_users.clear()

                if self.current_question >= self.questions_count:
                    result = self.end_game()
                    result["points"] = points
                    return result

                return {
                    "response": self.get_question(),
                    "points": points,
                    "next_question": True,
                }

        return None
