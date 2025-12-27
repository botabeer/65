import random
from games.base_game import BaseGame

class FastGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, theme=theme)
        self.game_name = "سريع"
        self.supports_hint = False
        self.supports_reveal = True
        
        self.phrases = [
            "سبحان الله", "الحمد لله", "الله اكبر", "لا اله الا الله",
            "استغفر الله", "لا حول ولا قوة الا بالله", "بسم الله",
            "يارب", "اللهم صل على محمد", "توكلت على الله",
            "ما شاء الله", "بارك الله فيك", "جزاك الله خيرا",
            "التوكل على الله طمأنينة", "العقل زينة الانسان",
            "الصبر مفتاح الفرج", "العلم نور", "من جد وجد",
            "احسن للناس تكن لهم خيرا", "الدعاء سلاح المؤمن",
            "الوقت كالسيف", "التقوى خير زاد", "احذر الغيبة",
            "السعادة في الرضا", "العفو من شيم الكرام",
            "الصدق منجاة", "الحياء من الايمان", "من تواضع لله رفعه"
        ]
        random.shuffle(self.phrases)
    
    def get_question(self):
        phrase = self.phrases[self.current_question % len(self.phrases)]
        self.current_answer = [phrase]
        
        return self.build_question_message(
            phrase,
            "اكتب العبارة بسرعة"
        )
    
    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.withdrawn_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if normalized == "ايقاف":
            return self.handle_withdrawal(user_id, display_name)
        
        if self.supports_reveal and normalized == "جاوب":
            return self.handle_reveal()
        
        if user_answer.strip() == self.current_answer[0]:
            return self.handle_correct_answer(user_id, display_name)
        
        return None
