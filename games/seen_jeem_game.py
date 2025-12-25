import random
from games.base_game import BaseGame

class SeenJeemGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "سين"
        self.supports_hint = True
        self.supports_reveal = True
        
        self.questions_data = [
            {"q": "ما هو الشيء الذي يمشي بلا رجلين ويبكي بلا عينين", "a": ["السحاب", "الغيم"]},
            {"q": "ما هو الشيء الذي له اسنان ولا يعض", "a": ["المشط"]},
            {"q": "ما هو الشيء الذي كلما زاد نقص", "a": ["العمر"]},
            {"q": "ما هو الشيء الذي يكتب ولا يقرا", "a": ["القلم"]},
            {"q": "ما هو الشيء الذي له عين ولا يرى", "a": ["الابرة", "الابره"]},
            {"q": "ما هو اطول نهر في العالم", "a": ["النيل"]},
            {"q": "ما هي عاصمة السعودية", "a": ["الرياض"]},
            {"q": "كم عدد ايام السنة", "a": ["365", "ثلاثمائة وخمسة وستون"]},
            {"q": "ما هو الحيوان الملقب بسفينة الصحراء", "a": ["الجمل"]},
            {"q": "كم عدد الوان قوس قزح", "a": ["7", "سبعة"]},
            {"q": "ما هو اكبر كوكب في المجموعة الشمسية", "a": ["المشتري"]},
            {"q": "كم عدد قارات العالم", "a": ["7", "سبعة"]},
            {"q": "ما هي اصغر دولة في العالم", "a": ["الفاتيكان"]},
            {"q": "كم عدد اسنان الانسان البالغ", "a": ["32", "اثنان وثلاثون"]},
            {"q": "ما هو اسرع حيوان بري", "a": ["الفهد"]},
            {"q": "كم عدد عظام جسم الانسان", "a": ["206", "مائتان وستة"]},
            {"q": "ما هي عاصمة فرنسا", "a": ["باريس"]},
            {"q": "كم عدد ايام الاسبوع", "a": ["7", "سبعة"]},
            {"q": "كم عدد اشهر السنة", "a": ["12", "اثنا عشر"]},
            {"q": "ما هي عاصمة مصر", "a": ["القاهرة", "القاهره"]},
            {"q": "من هو ابو الانبياء", "a": ["ابراهيم"]},
            {"q": "كم عدد ايام شهر رمضان", "a": ["29", "30", "تسعة وعشرون", "ثلاثون"]},
            {"q": "ما اسم اطول سورة في القران", "a": ["البقرة", "البقره"]},
            {"q": "في اي قارة تقع مصر", "a": ["افريقيا", "افريقيه"]},
            {"q": "كم عدد الصلوات المفروضة", "a": ["5", "خمسة", "خمس"]},
            {"q": "ما عاصمة الامارات", "a": ["ابوظبي", "ابو ظبي"]},
            {"q": "ما هو اكبر محيط في العالم", "a": ["الهادي", "الهادئ"]},
            {"q": "من مؤلف رواية البؤساء", "a": ["فيكتور هيجو", "فكتور هوجو"]},
            {"q": "كم عدد اركان الاسلام", "a": ["5", "خمسة", "خمس"]},
            {"q": "ما اسم اصغر دولة عربية", "a": ["البحرين"]},
            {"q": "ما هي عملة اليابان", "a": ["ين"]},
            {"q": "كم عدد لاعبي كرة القدم", "a": ["11", "احد عشر"]},
            {"q": "ما هي اكبر دولة في العالم", "a": ["روسيا"]},
            {"q": "من مخترع المصباح الكهربائي", "a": ["اديسون", "توماس اديسون"]},
            {"q": "ما هي عاصمة تركيا", "a": ["انقرة"]},
            {"q": "كم عدد حروف اللغة العربية", "a": ["28", "ثمانية وعشرون"]},
            {"q": "ما هي اصغر قارة في العالم", "a": ["استراليا"]},
            {"q": "من اول من صعد الى القمر", "a": ["نيل ارمسترونج", "ارمسترونج"]},
            {"q": "كم عدد اجنحة النحلة", "a": ["4", "اربعة"]},
            {"q": "ما هو لون دم الاخطبوط", "a": ["ازرق"]}
        ]
        
        random.shuffle(self.questions_data)
        self.used_questions = []

    def get_question(self):
        available = [q for q in self.questions_data if q not in self.used_questions]
        if not available:
            self.used_questions.clear()
            available = self.questions_data.copy()
        
        q_data = random.choice(available)
        self.used_questions.append(q_data)
        self.current_answer = q_data["a"]
        self.previous_question = q_data["q"]
        
        return self.build_question_message(q_data["q"])

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)
        
        if normalized in ["انسحب", "انسحاب"]:
            return self.handle_withdrawal(user_id, display_name)
        
        if self.supports_hint and normalized == "لمح":
            answer = self.current_answer[0]
            hint = f"يبدأ بحرف: {answer[0]}\nعدد الحروف: {len(answer)}"
            return {'response': self.build_text_message(hint), 'points': 0}

        if self.supports_reveal and normalized == "جاوب":
            answers = " او ".join(self.current_answer)
            self.previous_answer = answers
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                return self.end_game()
            
            return {'response': self.get_question(), 'points': 0, 'next_question': True}

        for correct_answer in self.current_answer:
            if self.normalize_text(correct_answer) == normalized:
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
