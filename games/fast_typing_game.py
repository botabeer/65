# games/fast_typing_game.py
import random
import time
from games.base_game import BaseGame

class FastGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, game_type="competitive", difficulty=difficulty, theme=theme)
        self.game_name = "اسرع"
        self.supports_hint = False
        self.supports_reveal = False
        self.round_time = self.difficulty_config["time"]
        self.round_start_time = None
        
        self.phrases = [
            "سبحان الله",
            "الحمد لله",
            "الله اكبر",
            "لا اله الا الله",
            "استغفر الله",
            "لا حول ولا قوة الا بالله",
            "بسم الله الرحمن الرحيم",
            "الله اعلم",
            "اللهم صل على محمد",
            "توكلت على الله",
            "حسبنا الله ونعم الوكيل",
            "ما شاء الله",
            "بارك الله فيك",
            "جزاك الله خيرا"
        ]
        
        self.used_phrases = []

    def get_question(self):
        available = [p for p in self.phrases if p not in self.used_phrases]
        
        if not available:
            self.used_phrases = []
            available = self.phrases.copy()
        
        phrase = random.choice(available)
        self.used_phrases.append(phrase)

        self.current_answer = phrase
        self.previous_question = f"اكتب: {phrase}"
        self.round_start_time = time.time()

        return self.build_question_message(
            f"اكتب:\n{phrase}",
            f"الوقت المتاح: {self.round_time} ثانية",
            show_timer=True
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active:
            return None
        
        if user_id in self.withdrawn_users:
            return None
        
        if user_id in self.answered_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        if normalized in ["انسحب", "انسحاب"]:
            return self.handle_withdrawal(user_id, display_name)

        elapsed = time.time() - self.round_start_time
        if elapsed > self.round_time:
            self.previous_answer = "انتهى الوقت"
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                return self.end_game()
            
            return {
                "response": self.get_question(),
                "points": 0,
                "next_question": True
            }

        if user_answer.strip() == self.current_answer:
            self.answered_users.add(user_id)
            
            time_bonus = max(0, int((self.round_time - elapsed) / 2))
            points = 1 + time_bonus
            
            earned = self.add_score(user_id, display_name, points)
            
            self.previous_answer = user_answer.strip()
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = earned
                return result
            
            return {
                "response": self.get_question(),
                "points": earned,
                "next_question": True
            }
        
        return None
