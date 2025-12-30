import random
from games.base_game import BaseGame

class OppositeGame(BaseGame):
    """لعبة الضد - ايجاد عكس الكلمة"""
    
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "ضد"
        self.supports_hint = True
        self.supports_reveal = True

        # 100 كلمة وأضدادها
        self.opposites = {
            "كبير": ["صغير"], "طويل": ["قصير"], "سريع": ["بطيء"],
            "ساخن": ["بارد"], "نظيف": ["وسخ"], "جديد": ["قديم"],
            "صعب": ["سهل"], "قوي": ["ضعيف"], "غني": ["فقير"],
            "سعيد": ["حزين"], "جميل": ["قبيح"], "ثقيل": ["خفيف"],
            "عالي": ["منخفض"], "واسع": ["ضيق"], "طيب": ["خبيث"],
            "شجاع": ["جبان"], "ذكي": ["غبي"], "بعيد": ["قريب"],
            "فوق": ["تحت"], "يمين": ["يسار"], "اول": ["اخر"],
            "كثير": ["قليل"], "رطب": ["جاف"], "مبتسم": ["عابس"],
            "نشيط": ["كسول"], "صادق": ["كاذب"], "لين": ["قاسي"],
            "مضيء": ["مظلم"], "حلو": ["مر"], "ناعم": ["خشن"],
            "صحيح": ["خطا"], "داخل": ["خارج"], "مفتوح": ["مغلق"],
            "ممتلئ": ["فارغ"], "شتاء": ["صيف"], "ليل": ["نهار"],
            "شرق": ["غرب"], "شمال": ["جنوب"], "امن": ["خطر"],
            "سلام": ["حرب"], "فرح": ["حزن"], "حياة": ["موت"],
            "صحة": ["مرض"], "نور": ["ظلام"], "حق": ["باطل"],
            "خير": ["شر"], "رحمة": ["عذاب"], "جنة": ["نار"],
            "ذكر": ["انثى"], "شباب": ["شيخوخة"], "غنى": ["فقر"],
            "جمال": ["قبح"], "عدل": ["ظلم"], "امل": ["ياس"],
            "حب": ["كره"], "صدق": ["كذب"], "علم": ["جهل"],
            "نظام": ["فوضى"], "سكون": ["حركة"], "يقين": ["شك"],
            "حق": ["واجب"], "فضيلة": ["رذيلة"], "حرية": ["عبودية"],
            "سعة": ["ضيق"], "كرم": ["بخل"], "شكر": ["كفر"],
            "تواضع": ["كبر"], "عزة": ["ذل"], "قوة": ["ضعف"],
            "صبر": ["جزع"], "رضا": ["سخط"], "امان": ["خوف"],
            "رخاء": ["شدة"], "نعمة": ["نقمة"], "بركة": ["محق"],
            "يسر": ["عسر"], "فرج": ["كرب"], "راحة": ["تعب"],
            "طمانينة": ["قلق"], "هدوء": ["ضجيج"], "صمت": ["كلام"],
            "ضحك": ["بكاء"], "فرح": ["ترح"], "سرور": ["حزن"],
            "بهجة": ["كابة"], "انشراح": ["ضيق"], "انبساط": ["انقباض"],
            "لذة": ["الم"], "متعة": ["شقاء"], "نعيم": ["عذاب"],
            "راحة": ["نصب"], "دعة": ["جهد"], "استرخاء": ["توتر"],
            "هناء": ["شقاء"], "سكينة": ["اضطراب"], "وقار": ["طيش"],
            "رزانة": ["خفة"], "حلم": ["عجلة"], "اناة": ["طيش"],
            "حكمة": ["حماقة"], "رشد": ["غي"], "هدى": ["ضلال"]
        }

        self.questions_list = list(self.opposites.items())
        random.shuffle(self.questions_list)
        self.used_questions_indices = []

    def get_question(self):
        available_indices = [
            i for i in range(len(self.questions_list))
            if i not in self.used_questions_indices
        ]
        
        if not available_indices:
            self.used_questions_indices = []
            available_indices = list(range(len(self.questions_list)))
            random.shuffle(self.questions_list)
        
        question_idx = random.choice(available_indices)
        self.used_questions_indices.append(question_idx)
        
        word, answers = self.questions_list[question_idx]
        
        self.current_answer = answers
        self.previous_question = f"ما عكس: {word}"
        
        return self.build_question_message(f"ما عكس كلمة:\n{word}")

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)

        if normalized == "ايقاف":
            return self.handle_withdrawal(user_id, display_name)

        if self.supports_hint and normalized == "لمح":
            hint_answer = self.current_answer[0]
            return {
                "response": self.build_text_message(
                    f"يبدا ب: {hint_answer[0]}\nعدد الحروف: {len(hint_answer)}"
                ),
                "points": 0
            }

        if self.supports_reveal and normalized == "جاوب":
            self.previous_answer = self.current_answer[0]
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                return self.end_game()
            
            return {
                "response": self.get_question(),
                "points": 0,
                "next_question": True
            }

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
                
                return {
                    "response": self.get_question(),
                    "points": points,
                    "next_question": True
                }

        return None
