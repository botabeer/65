import random
from games.base_game import BaseGame

class IqGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "ذكاء"

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
            {"q": "ما هو الشيء الذي يوجد في السماء وإذا اضفت له حرف اصبح في الارض", "a": ["نجم"]},
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
            {"q": "ما هو الشيء الذي تراه في الليل ثلاث مرات وفي النهار مرة واحدة", "a": ["اللام"]},
            {"q": "ماذا يقول الجدار للجدار", "a": ["سنلتقي في الزاوية"]},
            {"q": "شيء له رقبة وليس له راس", "a": ["الزجاجة"]},
            {"q": "ما هو الذي يكون اخضر في الارض واسود في السوق واحمر في البيت", "a": ["الشاي"]},
            {"q": "رقم اذا ضرب في الرقم الذي يليه كان حاصل الضرب يساوي ناتج جمعهما زائد 11", "a": ["اربعة", "4"]},
            {"q": "شيء تملكه ولكن غيرك يستخدمه اكثر منك", "a": ["الاسم"]},
            {"q": "انا ابن الماء فإن تركوني في الماء مت", "a": ["الثلج"]},
            {"q": "ما هو القبر الذي سار بصاحبه", "a": ["الحوت"]},
            {"q": "يمشي ويقف وليس له ارجل", "a": ["الساعة"]},
            {"q": "كلي ثقوب ومع ذلك احفظ الماء", "a": ["الاسفنج"]},
            {"q": "ابن امك وابن ابيك وليس باختك ولا باخيك", "a": ["انت"]},
            {"q": "عائلة مؤلفة من 6 بنات واخ لكل منهن كم عدد افراد العائلة", "a": ["سبعة", "7"]},
            {"q": "انا في المدينة وليس في القرية", "a": ["حرف الدال", "الدال"]}
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
        return self.build_question_message(riddle["q"])

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)

        if normalized in ["ايقاف", "ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)

        for correct in self.current_answer:
            if self.normalize_text(correct) == normalized:
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
