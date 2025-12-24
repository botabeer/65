from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from .base_game import BaseGame

class SeenJeemGame(BaseGame):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api, questions_count=5)
        self.game_name = "سين جيم"
        
        self.questions_data = [
            {"q": "ما هو الشيء الذي يمشي بلا رجلين ويبكي بلا عينين", "a": "السحاب"},
            {"q": "ما هو الشيء الذي له اسنان ولا يعض", "a": "المشط"},
            {"q": "ما هو الشيء الذي كلما زاد نقص", "a": "العمر"},
            {"q": "ما هو الشيء الذي يكتب ولا يقرا", "a": "القلم"},
            {"q": "ما هو الشيء الذي له عين ولا يرى", "a": "الابرة"},
            {"q": "ما هو اطول نهر في العالم", "a": "النيل"},
            {"q": "ما هي عاصمة السعودية", "a": "الرياض"},
            {"q": "كم عدد ايام السنة", "a": "365"},
            {"q": "ما هو الحيوان الملقب بسفينة الصحراء", "a": "الجمل"},
            {"q": "كم عدد الوان قوس قزح", "a": "7"},
            {"q": "ما هو اكبر كوكب في المجموعة الشمسية", "a": "المشتري"},
            {"q": "كم عدد قارات العالم", "a": "7"},
            {"q": "ما هي اصغر دولة في العالم", "a": "الفاتيكان"},
            {"q": "كم عدد اسنان الانسان البالغ", "a": "32"},
            {"q": "ما هو اسرع حيوان بري", "a": "الفهد"},
            {"q": "كم عدد عظام جسم الانسان", "a": "206"},
            {"q": "ما هي عاصمة فرنسا", "a": "باريس"},
            {"q": "كم عدد ايام الاسبوع", "a": "7"},
            {"q": "كم عدد اشهر السنة", "a": "12"},
            {"q": "ما هي عاصمة مصر", "a": "القاهرة"}
        ]
        
        random.shuffle(self.questions_data)

    def get_question(self):
        q_data = self.questions_data[self.current_question % len(self.questions_data)]
        self.current_answer = [q_data["a"]]
        
        return self.build_question_message(q_data["q"])

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)
        
        if self.supports_hint and normalized == "لمح":
            answer = self.current_answer[0]
            hint = f"يبدا بحرف: {answer[0]}\nعدد الحروف: {len(answer)}"
            return {'response': self.build_text_message(hint), 'points': 0}

        if self.supports_reveal and normalized == "جاوب":
            reveal = f"الاجابة: {self.current_answer[0]}"
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["message"] = f"{reveal}\n\n{result.get('message', '')}"
                return result
            
            return {'response': self.build_text_message(reveal), 'points': 0, 'next_question': True}

        correct_answer = self.normalize_text(self.current_answer[0])

        if normalized == correct_answer or normalized in correct_answer or correct_answer in normalized:
            points = self.add_score(user_id, display_name, 1)
            self.current_question += 1
            self.answered_users.clear()

            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result

            return {'response': self.build_text_message(f"اجابة صحيحة {display_name}\n+{points}"), 'points': points, 'next_question': True}

        return None
