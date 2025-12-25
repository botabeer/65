import random
from games.base_game import BaseGame

class RouletteGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, game_type="competitive", difficulty=difficulty, theme=theme)
        self.game_name = "روليت"
        self.supports_hint = True
        self.supports_reveal = True
        
        self.roulette_numbers = list(range(0, 37))
        self.red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        self.black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        
        self.current_spin_result = None
        self.last_spin_result = None
    
    def spin_roulette(self):
        return random.choice(self.roulette_numbers)
    
    def get_color(self, number):
        if number == 0:
            return "اخضر"
        elif number in self.red_numbers:
            return "احمر"
        else:
            return "اسود"
    
    def get_question(self):
        self.current_spin_result = self.spin_roulette()
        result_color = self.get_color(self.current_spin_result)
        self.current_answer = [str(self.current_spin_result), result_color]
        
        message = "تدور الروليت\n\nخمن الرقم او اللون"
        
        if self.last_spin_result is not None:
            last_color = self.get_color(self.last_spin_result)
            message += f"\n\nالدورة السابقة:\nالرقم: {self.last_spin_result}\nاللون: {last_color}"
        
        subtitle = "خمن الرقم او اللون او زوجي او فردي"
        self.previous_question = "دورة الروليت"
        
        return self.build_question_message(message, subtitle)
    
    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if normalized in ["ايقاف", "ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)
        
        if self.supports_hint and normalized == "لمح":
            result_color = self.get_color(self.current_spin_result)
            is_even = self.current_spin_result % 2 == 0 and self.current_spin_result != 0
            hint = f"اللون: {result_color}\n{'زوجي' if is_even else 'فردي' if self.current_spin_result != 0 else 'صفر'}"
            return {"response": self.build_text_message(hint), "points": 0}
        
        if self.supports_reveal and normalized == "جاوب":
            reveal = f"الرقم: {self.current_spin_result}\nاللون: {self.get_color(self.current_spin_result)}"
            self.previous_answer = reveal
            self.last_spin_result = self.current_spin_result
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                return self.end_game()
            
            return {"response": self.get_question(), "points": 0, "next_question": True}
        
        won = False
        
        try:
            guess_number = int(user_answer.strip())
            if 0 <= guess_number <= 36 and guess_number == self.current_spin_result:
                won = True
        except ValueError:
            pass
        
        if not won:
            result_color = self.get_color(self.current_spin_result)
            if (normalized == "احمر" and result_color == "احمر") or \
               (normalized == "اسود" and result_color == "اسود") or \
               (normalized == "اخضر" and result_color == "اخضر"):
                won = True
        
        if not won and self.current_spin_result != 0:
            is_even = self.current_spin_result % 2 == 0
            if (normalized == "زوجي" and is_even) or (normalized == "فردي" and not is_even):
                won = True
        
        if won:
            self.answered_users.add(user_id)
            points = self.add_score(user_id, display_name, 1)
            
            self.previous_answer = f"{self.current_spin_result} - {self.get_color(self.current_spin_result)}"
            self.last_spin_result = self.current_spin_result
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
