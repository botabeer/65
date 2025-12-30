import random
from games.base_game import BaseGame

class LetterGame(BaseGame):
    """لعبة الحروف - اسئلة تبدأ بحرف معين"""
    
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "حرف"
        self.supports_hint = True
        self.supports_reveal = True
        
        # قاعدة بيانات الأسئلة مرتبة حسب الحروف
        self.questions_db = {
            "ا": [
                {"q": "من هو اول نبي", "a": ["آدم", "ادم"]},
                {"q": "ما هي عاصمة اليونان", "a": ["أثينا", "اثينا"]},
                {"q": "ما هي عاصمة الجزائر", "a": ["الجزائر"]},
                {"q": "من هو اول خليفة للمسلمين", "a": ["أبو بكر", "ابو بكر", "ابوبكر"]},
                {"q": "ما هي اكبر قارة في العالم", "a": ["آسيا", "اسيا"]}
            ],
            "ب": [
                {"q": "ما هي عاصمة العراق", "a": ["بغداد"]},
                {"q": "ما هي عاصمة الصين", "a": ["بكين"]},
                {"q": "ما هي عاصمة لبنان", "a": ["بيروت"]},
                {"q": "ما هي عاصمة ألمانيا", "a": ["برلين"]},
                {"q": "ما الحيوان المعروف بتزويدنا بالحليب", "a": ["بقرة"]}
            ],
            "ت": [
                {"q": "ما هي عاصمة تونس", "a": ["تونس"]},
                {"q": "ما هي عاصمة تايوان", "a": ["تايبيه", "تايبي"]},
                {"q": "ما هي عاصمة جورجيا", "a": ["تبليسي"]},
                {"q": "ما الحيوان الضخم الذي يعيش في المستنقعات", "a": ["تمساح"]},
                {"q": "ما الفاكهة التي تأتي بألوان مختلفة", "a": ["تفاح"]}
            ],
            "ج": [
                {"q": "ما هي عاصمة جيبوتي", "a": ["جيبوتي"]},
                {"q": "ما المدينة السعودية على البحر الأحمر", "a": ["جدة", "جده"]},
                {"q": "ما الحيوان المعروف بسفينة الصحراء", "a": ["جمل"]},
                {"q": "من الصحابي الذي قاد المسلمين الى الحبشة", "a": ["جعفر"]},
                {"q": "ما اكبر كوكب في المجموعة الشمسية", "a": ["جوبيتر", "المشتري"]}
            ],
            "ح": [
                {"q": "ما المدينة السورية المشهورة بقلعتها", "a": ["حلب"]},
                {"q": "ما المدينة السورية التي يمر بها نهر العاصي", "a": ["حماة", "حماه"]},
                {"q": "ما المدينة السعودية في شمال المملكة", "a": ["حائل"]},
                {"q": "ما الركن الخامس من اركان الاسلام", "a": ["حج"]},
                {"q": "ما الحيوان العملاق الذي يعيش في المحيطات", "a": ["حوت"]}
            ],
            "د": [
                {"q": "ما هي عاصمة ايرلندا", "a": ["دبلن"]},
                {"q": "ما هي عاصمة سوريا", "a": ["دمشق"]},
                {"q": "ما المدينة الاماراتية الشهيرة", "a": ["دبي"]},
                {"q": "ما هي عاصمة قطر", "a": ["دوحة", "الدوحة"]},
                {"q": "ما الحيوان الذي يعيش في القطب الشمالي", "a": ["دب قطبي", "دب"]}
            ],
            "ر": [
                {"q": "ما هي عاصمة ايطاليا", "a": ["روما"]},
                {"q": "ما الدولة الاكبر مساحة في العالم", "a": ["روسيا"]},
                {"q": "ما هي عاصمة ايسلندا", "a": ["ريكيافيك"]},
                {"q": "ما اسم العملة الرسمية في قطر", "a": ["ريال قطري", "ريال"]},
                {"q": "من ابنة الرسول التي تزوجها عثمان", "a": ["رقية"]}
            ],
            "س": [
                {"q": "ما الحيوان الزاحف البطيء ذو الصدفة", "a": ["سلحفاة", "سلحفاه"]},
                {"q": "من الصحابي الذي اشار بحفر الخندق", "a": ["سلمان الفارسي", "سلمان"]},
                {"q": "ما هي عاصمة السويد", "a": ["ستوكهولم"]},
                {"q": "ما الحيوان الصغير الذي يعيش على الاشجار", "a": ["سنجاب"]},
                {"q": "ما الدولة العربية التي عاصمتها مسقط", "a": ["سلطنة عمان", "عمان"]}
            ],
            "ع": [
                {"q": "ما المادة الحلوة التي ينتجها النحل", "a": ["عسل"]},
                {"q": "ما العضو في جسم الانسان للرؤية", "a": ["عين"]},
                {"q": "ما هي عاصمة الاردن", "a": ["عمان"]},
                {"q": "ما القدرة على التفكير والتحليل", "a": ["عقل"]},
                {"q": "ما الفاكهة التي تزرع في كروم", "a": ["عنب"]}
            ],
            "ف": [
                {"q": "ما الدولة الاوروبية عاصمتها هلسنكي", "a": ["فنلندا"]},
                {"q": "ما الدولة الاوروبية عاصمتها باريس", "a": ["فرنسا"]},
                {"q": "ما الحيوان البري الاكبر حجما في افريقيا", "a": ["فيل"]},
                {"q": "ما الحيوان الاسرع في العدو", "a": ["فهد"]},
                {"q": "ما الامبراطورية التي امتدت في ايران", "a": ["فارس"]}
            ],
            "ق": [
                {"q": "ما الدولة العربية على الخليج", "a": ["قطر"]},
                {"q": "ما هي عاصمة مصر", "a": ["قاهرة", "القاهرة"]},
                {"q": "ما المدينة الجزائرية بجسورها المعلقة", "a": ["قسنطينة"]},
                {"q": "ما اكبر قارة من حيث المساحة", "a": ["آسيا", "اسيا"]},
                {"q": "ما الكائن البحري الهلامي", "a": ["قنديل البحر", "قنديل"]}
            ],
            "ك": [
                {"q": "ما هي عاصمة ماليزيا", "a": ["كوالالمبور"]},
                {"q": "ما هي عاصمة افغانستان", "a": ["كابول"]},
                {"q": "ما هي عاصمة اوكرانيا", "a": ["كييف"]},
                {"q": "ما هي عاصمة اوغندا", "a": ["كمبالا"]},
                {"q": "ما البناء المقدس في مكة", "a": ["كعبة", "الكعبة"]}
            ],
            "م": [
                {"q": "ما العضو الذي يتحكم في الوظائف الحيوية", "a": ["مخ"]},
                {"q": "ما الشركة التي تصنع سيارات فاخرة", "a": ["مرسيدس"]},
                {"q": "ما العضو الذي يساعد في التنسيق", "a": ["مخيخ"]},
                {"q": "ما الجهاز المستخدم في الزراعة", "a": ["محراث"]},
                {"q": "ما العضو الذي يساعد في هضم الطعام", "a": ["معدة", "المعدة"]}
            ],
            "ن": [
                {"q": "ما اكبر نهر في العالم", "a": ["نيل", "النيل"]},
                {"q": "ما الطائر الذي يرمز الى الحرية", "a": ["نسر"]},
                {"q": "ما الحيوان رمز القوة", "a": ["نمر"]},
                {"q": "ما الضوء الذي يشع من الشمس", "a": ["نور"]},
                {"q": "ما المادة المالية في المعاملات", "a": ["نقود"]}
            ],
            "ي": [
                {"q": "ما الفترة الزمنية التي تبلغ 24 ساعة", "a": ["يوم"]},
                {"q": "ما العضو المستخدم للمس والامساك", "a": ["يد"]},
                {"q": "ما الشعور بالثقة التامة", "a": ["يقين"]},
                {"q": "ما الاتجاه المعاكس لليمين", "a": ["يسار"]},
                {"q": "ما الدولة العربية في جنوب الجزيرة", "a": ["يمن", "اليمن"]}
            ]
        }
        
        # قائمة الحروف المتاحة
        self.letters = list(self.questions_db.keys())
        random.shuffle(self.letters)
        
        # استخدام قاموس لتتبع الأسئلة المستخدمة لكل حرف
        self.used_questions = {letter: [] for letter in self.letters}
        
        # متغيرات اللعبة
        self.current_letter = None
        self.current_question_data = None

    def get_question(self):
        """الحصول على السؤال التالي"""
        # اختيار الحرف بناء على رقم السؤال
        letter_idx = self.current_question % len(self.letters)
        self.current_letter = self.letters[letter_idx]
        
        # الحصول على الأسئلة المتاحة لهذا الحرف
        available_indices = [
            i for i in range(len(self.questions_db[self.current_letter]))
            if i not in self.used_questions[self.current_letter]
        ]
        
        # إعادة تعيين الأسئلة المستخدمة إذا انتهت
        if not available_indices:
            self.used_questions[self.current_letter] = []
            available_indices = list(range(len(self.questions_db[self.current_letter])))
        
        # اختيار سؤال عشوائي
        question_idx = random.choice(available_indices)
        self.used_questions[self.current_letter].append(question_idx)
        
        self.current_question_data = self.questions_db[self.current_letter][question_idx]
        
        # تعيين الإجابات الصحيحة
        self.current_answer = self.current_question_data['a']
        self.previous_question = f"حرف {self.current_letter}: {self.current_question_data['q']}"
        
        return self.build_question_message(
            f"حرف: {self.current_letter}\n\n{self.current_question_data['q']}",
            f"الاجابة تبدا بحرف {self.current_letter}"
        )

    def check_answer(self, user_answer, user_id, display_name):
        """التحقق من الإجابة"""
        if not self.game_active or user_id in self.answered_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        # إيقاف اللعبة
        if normalized == "ايقاف":
            return self.handle_withdrawal(user_id, display_name)
        
        # التلميح
        if self.supports_hint and normalized == "لمح":
            answer = self.current_answer[0]
            hint = f"يبدا بحرف: {answer[0]}\nعدد الحروف: {len(answer)}"
            return {"response": self.build_text_message(hint), "points": 0}
        
        # إظهار الجواب
        if self.supports_reveal and normalized == "جاوب":
            answers = " او ".join(self.current_answer)
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
        
        # التحقق من الإجابة الصحيحة
        for correct_answer in self.current_answer:
            normalized_correct = self.normalize_text(correct_answer)
            if normalized == normalized_correct:
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
