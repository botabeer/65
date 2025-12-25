import random
from games.base_game import BaseGame

class ScrambleGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "ترتيب"

        self.words = [
            "مدرسة","كتاب","قلم","باب","نافذة","طاولة","كرسي",
            "سيارة","طائرة","حديقة","شجرة","وردة","فراشة","نملة",
            "سمكة","حوت","نجمة","قمر","شمس","سحابة","مطر","برق",
            "رعد","ثلج","جبل","بحر","نهر","صحراء","جزيرة","واحة",
            "مدينة","قرية","بيت","مسجد","كنيسة","مستشفى","جامعة",
            "مكتبة","متحف","سوق","ملعب","مسبح","مطار","محطة",
            "جسر","طريق","شارع","ميدان"
        ]

        random.shuffle(self.words)
        self.used_words = []

    def scramble_word(self, word):
        letters = list(word)
        random.shuffle(letters)
        return " ".join(letters)

    def get_question(self):
        available = [w for w in self.words if w not in self.used_words]
        
        if not available:
            self.used_words = []
            available = self.words.copy()
            random.shuffle(available)

        word = random.choice(available)
        self.used_words.append(word)

        self.current_answer = word
        return self.build_question_message(
            f"رتب الحروف:\n{self.scramble_word(word)}"
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        answer = self.normalize_text(user_answer)

        if answer in ["ايقاف", "ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)

        if answer == self.normalize_text(self.current_answer):
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
