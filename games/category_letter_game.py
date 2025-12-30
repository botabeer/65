import random
from games.base_game import BaseGame
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer

class CategoryGame(BaseGame):
    """لعبة الفئة - اجب بكلمة من فئة معينة تبدأ بحرف معين"""
    
    def __init__(self, line_bot_api, theme='light'):
        super().__init__(line_bot_api, theme=theme)
        self.game_name = "فئه"
        self.questions_count = 5
        self.supports_hint = True
        self.supports_reveal = True
        
        # 100 تحدي متنوع
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
            {"category": "جهاز منزلي", "letter": "غ", "answers": ["غسالة", "غلاية"]},
            {"category": "عطر", "letter": "ع", "answers": ["عود", "عنبر"]},
            {"category": "معجنات", "letter": "ف", "answers": ["فطيرة", "فتة"]},
            {"category": "مشروب ساخن", "letter": "ش", "answers": ["شاي", "شوكولاتة"]},
            {"category": "حلوى شعبية", "letter": "ك", "answers": ["كنافة", "كعك"]},
            {"category": "اداة", "letter": "م", "answers": ["مطرقة", "منشار"]},
            {"category": "لعبة", "letter": "ش", "answers": ["شطرنج", "شبكة"]},
            {"category": "الة موسيقية", "letter": "ع", "answers": ["عود", "عصا"]},
            {"category": "مكان عبادة", "letter": "م", "answers": ["مسجد", "معبد"]},
            {"category": "حيوان مفترس", "letter": "ا", "answers": ["اسد", "ارنب"]},
            {"category": "طير جارح", "letter": "ص", "answers": ["صقر", "صرد"]},
            {"category": "سمك", "letter": "ت", "answers": ["تونة", "تونا"]},
            {"category": "خضار", "letter": "ب", "answers": ["بصل", "باذنجان"]},
            {"category": "فاكهة استوائية", "letter": "م", "answers": ["مانجو", "موز"]},
            {"category": "مكسرات", "letter": "ل", "answers": ["لوز", "لب"]},
            {"category": "بهارات", "letter": "ك", "answers": ["كمون", "كركم"]},
            {"category": "اداة طبخ", "letter": "س", "answers": ["سكين", "ساطور"]},
            {"category": "مشروب بارد", "letter": "ع", "answers": ["عصير", "عرقسوس"]},
            {"category": "وجبة", "letter": "غ", "answers": ["غداء", "غبقة"]},
            {"category": "لحم", "letter": "د", "answers": ["دجاج", "ديك"]},
            {"category": "سلطة", "letter": "ف", "answers": ["فتوش", "فواكه"]},
            {"category": "شوربة", "letter": "ع", "answers": ["عدس", "عظم"]},
            {"category": "معكرونة", "letter": "ب", "answers": ["باستا", "بيني"]},
            {"category": "خبز", "letter": "ت", "answers": ["تميس", "تنور"]},
            {"category": "جبنة", "letter": "ح", "answers": ["حلوم", "حلومي"]},
            {"category": "صلصة", "letter": "ط", "answers": ["طماطم", "طحينة"]},
            {"category": "حلى", "letter": "ب", "answers": ["بودينج", "بسكويت"]},
            {"category": "ايس كريم", "letter": "ف", "answers": ["فانيلا", "فراولة"]},
            {"category": "كيك", "letter": "ش", "answers": ["شوكولاتة", "شيز"]},
            {"category": "بسكويت", "letter": "ا", "answers": ["اوريو", "اولكر"]},
            {"category": "شوكولاتة", "letter": "ك", "answers": ["كادبوري", "كيت كات"]},
            {"category": "حلوى غربية", "letter": "د", "answers": ["دونات", "دوريتوس"]},
            {"category": "مربى", "letter": "ت", "answers": ["توت", "تين"]},
            {"category": "عسل", "letter": "س", "answers": ["سدر", "سمر"]},
            {"category": "زيت", "letter": "ز", "answers": ["زيتون", "زهرة"]},
            {"category": "خل", "letter": "ت", "answers": ["تفاح", "تمر"]},
            {"category": "ملح", "letter": "ب", "answers": ["بحر", "بحري"]},
            {"category": "سكر", "letter": "ن", "answers": ["نبات", "ناعم"]},
            {"category": "دقيق", "letter": "ا", "answers": ["ابيض", "اسمر"]},
            {"category": "ارز", "letter": "ب", "answers": ["بسمتي", "بني"]},
            {"category": "مكرونة", "letter": "م", "answers": ["معكرونة", "مكرونة"]},
            {"category": "قهوة", "letter": "ع", "answers": ["عربية", "عربي"]},
            {"category": "شاي", "letter": "ا", "answers": ["احمر", "اخضر"]},
            {"category": "عصير", "letter": "ب", "answers": ["برتقال", "بطيخ"]},
            {"category": "ماء", "letter": "م", "answers": ["معدني", "مفلتر"]},
            {"category": "حليب", "letter": "ك", "answers": ["كامل", "كامل الدسم"]},
            {"category": "لبن", "letter": "ر", "answers": ["روب", "رائب"]},
            {"category": "قشطة", "letter": "ط", "answers": ["طازج", "طازجة"]},
            {"category": "زبدة", "letter": "ح", "answers": ["حيوانية", "حليب"]},
            {"category": "سمنة", "letter": "ب", "answers": ["بلدي", "بقري"]},
            {"category": "بيض", "letter": "د", "answers": ["دجاج", "دواجن"]},
            {"category": "لحم", "letter": "غ", "answers": ["غنم", "غزال"]},
            {"category": "سمك", "letter": "ه", "answers": ["هامور", "هامر"]},
            {"category": "دجاج", "letter": "م", "answers": ["محمر", "مشوي"]},
            {"category": "ربيان", "letter": "ج", "answers": ["جمبري", "جامبو"]},
            {"category": "كبدة", "letter": "د", "answers": ["دجاج", "ديك"]},
            {"category": "نقانق", "letter": "ح", "answers": ["حار", "حراق"]},
            {"category": "همبرجر", "letter": "ل", "answers": ["لحم", "لحمة"]},
            {"category": "بيتزا", "letter": "ج", "answers": ["جبن", "جبنة"]}
        ]
        
        self.used_challenges = []

    def get_question(self):
        available = [
            c for c in self.challenges
            if c not in self.used_challenges
        ]
        
        if not available:
            self.used_challenges = []
            available = self.challenges.copy()
            random.shuffle(available)
        
        challenge = random.choice(available)
        self.used_challenges.append(challenge)
        
        self.current_answer = challenge["answers"]
        self.previous_question = f"{challenge['category']} حرف {challenge['letter']}"
        
        return self.build_question_message(
            f"الفئة: {challenge['category']}\nالحرف: {challenge['letter']}",
            "اكتب اي كلمة مناسبة"
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)

        if normalized == "ايقاف":
            return self.handle_withdrawal(user_id, display_name)

        if self.supports_hint and normalized == "لمح":
            sample = self.current_answer[0]
            hint = f"يبدا بحرف: {sample[0]}\nعدد الحروف: {len(sample)}"
            return {"response": self.build_text_message(hint), "points": 0}

        if self.supports_reveal and normalized == "جاوب":
            answers = " - ".join(self.current_answer)
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

        valid_answers = [self.normalize_text(a) for a in self.current_answer]
        
        if normalized in valid_answers:
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
