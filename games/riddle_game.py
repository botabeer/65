import random
from games.base_game import BaseGame

class RiddleGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "لغز"
        self.supports_hint = True
        self.supports_reveal = True

        self.riddles = [
            {"q": "ما الشيء الذي يمشي بلا ارجل ويبكي بلا عيون", "a": ["السحاب", "الغيم"]},
            {"q": "له راس ولكن لا عين له", "a": ["الدبوس", "المسمار"]},
            {"q": "شيء كلما زاد نقص", "a": ["العمر"]},
            {"q": "يكتب ولا يقرا ابدا", "a": ["القلم"]},
            {"q": "له اسنان كثيرة ولكنه لا يعض", "a": ["المشط"]},
            {"q": "يوجد في الماء ولكن الماء يميته", "a": ["الملح"]},
            {"q": "يتكلم بجميع اللغات دون ان يتعلمها", "a": ["الصدى"]},
            {"q": "شيء كلما اخذت منه كبر", "a": ["الحفرة"]},
            {"q": "يخترق الزجاج ولا يكسره", "a": ["الضوء"]},
            {"q": "يسمع بلا اذن ويتكلم بلا لسان", "a": ["الهاتف"]},
            {"q": "له عين ولا يرى", "a": ["الابرة"]},
            {"q": "يجري ولا يمشي", "a": ["الماء", "النهر"]},
            {"q": "اخ لأبيك وليس عمك", "a": ["ابي", "والدي"]},
            {"q": "ما الذي يحدث مرة في الدقيقة ومرتين في اللحظة ولا يحدث في الساعة", "a": ["القاف"]},
            {"q": "حامل ومحمول نصفه ناشف ونصفه مبلول", "a": ["السفينة"]},
            {"q": "ترى كل شيء وليس لها عيون", "a": ["المراة"]},
            {"q": "ما هو الشيء الذي اسمه على لونه", "a": ["البيضة"]},
            {"q": "له اربع ارجل ولا يستطيع المشي", "a": ["الطاولة", "الكرسي"]},
            {"q": "اذا اكلته كله تستفيد واذا اكلت نصفه تموت", "a": ["السمسم"]},
            {"q": "ما هو الطائر الذي يلد ولا يبيض", "a": ["الخفاش"]},
            {"q": "من هو الخال الوحيد لأولاد عمتك", "a": ["ابي", "والدي"]},
            {"q": "يسير بلا رجلين ولا يدخل الا بالاذنين", "a": ["الصوت"]},
            {"q": "ما هو البيت الذي ليس له ابواب ولا نوافذ", "a": ["بيت الشعر"]},
            {"q": "كلمة تتكون من 8 حروف ولكنها تجمع كل الحروف", "a": ["ابجدية"]},
            {"q": "شيء اذا غليته جمد", "a": ["البيض"]},
            {"q": "شيء له رقبة وليس له راس", "a": ["الزجاجة"]},
            {"q": "ما هو الذي يكون اخضر في الارض واسود في السوق واحمر في البيت", "a": ["الشاي"]},
            {"q": "شيء تملكه ولكن غيرك يستخدمه اكثر منك", "a": ["الاسم"]},
            {"q": "انا ابن الماء فإن تركوني في الماء مت", "a": ["الثلج"]},
            {"q": "ما هو القبر الذي سار بصاحبه", "a": ["الحوت"]},
            {"q": "يمشي ويقف وليس له ارجل", "a": ["الساعة"]},
            {"q": "كلي ثقوب ومع ذلك احفظ الماء", "a": ["الاسفنج"]},
            {"q": "ابن امك وابن ابيك وليس باختك ولا باخيك", "a": ["انت"]},
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

        random.shuffle(self.riddles)
        self.used_riddles = []

    def get_question(self):
        available = [r for r in self.riddles if r not in self.used_riddles]
        if not available:
            self.used_riddles = []
            available = self.riddles.copy()
            random.shuffle(available)

        riddle = random.choice(available)
        self.used_riddles.append(riddle)
        self.current_answer = riddle["a"]
        self.previous_question = riddle["q"]
        
        return self.build_question_message(riddle["q"])

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)

        if normalized in ["ايقاف", "ايقاف"]:
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

        for correct in self.current_answer:
            if self.normalize_text(correct) == normalized:
                self.answered_users.add(user_id)
                points = self.add_score(user_id, display_name, 1)
                self.previous_answer = user_answer.strip()
                self.current_question += 1
                self.answered_users.clear()

                if self.current_question >= self.questions_count:
                    result = self.end_game()
                    result["points"] = points
                    return result

                return {'response': self.get_question(), 'points': points, 'next_question': True}

        return None
