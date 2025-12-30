import random
from games.base_game import BaseGame

class ScrambleGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=1, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "ترتيب"
        self.supports_hint = True
        self.total_questions = 5  # عدد الأسئلة لكل لعبة

        # خمس مستويات صعوبة مع كلمات حقيقية
        self.difficulty_levels = {
            1: ["قلم","باب","كتاب","وردة","شمس","قمر","نهر","بيت","نملة","سمكة"],
            2: ["مدرسة","مستشفى","جامعة","مكتبة","متحف","مطار","محطة","ملعب","مسبح","سوق"],
            3: ["مكتبة_جامعية","مركز_تجاري","مستشفى_خاص","مسجد_جامع","كنيسة_قديمة",
                "نهر_الأردن","بحيرة_طبريا","جبل_المرتفعات","حديقة_الوطن","ساحة_الشهداء"],
            4: ["قمر_الليل","نجمة_الصحراء","مطر_الربيع","ثلج_الشتاء","سحابة_السماء",
                "سمكة_النهر","حوت_المحيط","فراشة_الحديقة","نملة_الغابة","كرسي_الحديقة"],
            5: ["مدينة_التاريخ","قرية_العراقة","مستشفى_المدينة","جامعة_العلم","مركز_البحث",
                "ساحة_الثقافة","جسر_الحضارة","برج_المجد","قصر_الأساطير","مكتبة_التراث"]
        }

        self.used_words = []
        self.current_answer = ""
        self.current_question = 0
        self.answered_users = set()
        self.game_active = False
        self.current_level = difficulty
        self.hint_count = 0

    def scramble_word(self, word):
        letters = list(word)
        random.shuffle(letters)
        return " ".join(letters)

    def start_game(self):
        self.game_active = True
        self.current_question = 0
        self.answered_users.clear()
        self.hint_count = 0
        self.used_words = []
        return self.get_question()

    def get_question(self):
        # اختر الكلمة حسب المستوى الحالي بدون تكرار
        level_words = [w for w in self.difficulty_levels[self.current_level] if w not in self.used_words]

        if not level_words:
            self.used_words = []
            level_words = self.difficulty_levels[self.current_level].copy()
            random.shuffle(level_words)

        word = random.choice(level_words)
        self.used_words.append(word)
        self.current_answer = word
        self.current_question += 1
        self.hint_count = 0  # إعادة عداد التلميح لكل سؤال جديد

        return self.build_question_message(
            f"رتب الحروف:\n{self.scramble_word(word)}"
        )

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.answered_users:
            return None

        normalized = self.normalize_text(user_answer)

        # أمر الإيقاف
        if normalized in ["ايقاف", "ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)

        # التلميح التدريجي
        if self.supports_hint and normalized == "لمح":
            self.hint_count += 1
            first_char = self.current_answer[0]
            length = len(self.current_answer.replace("_", " "))
            words = self.current_answer.split("_")

            if self.hint_count == 1:
                hint = f"أول حرف: {first_char}, عدد الحروف: {length}"
            elif self.hint_count == 2:
                hint = f"أول حرف: {first_char}, عدد الحروف: {length}, كلمة: {words[0]}"
            else:
                hint = f"أول حرف: {first_char}, عدد الحروف: {length}, كلمة/كلمتين: {' '.join(words)}"

            return {"response": self.build_text_message(hint), "points": 0}

        # إظهار الإجابة عند "جاوب"
        if normalized == "جاوب":
            answer_text = self.current_answer.replace("_", " ")
            return {"response": self.build_text_message(f"الإجابة الصحيحة: {answer_text}"), "points": 0}

        # التحقق من الإجابة الصحيحة
        if normalized == self.normalize_text(self.current_answer):
            points = self.add_score(user_id, display_name, 1)
            self.answered_users.clear()
            self.hint_count = 0

            # إذا وصلنا للسؤال الأخير نعلن الفائز مباشرة
            if self.current_question >= self.total_questions:
                self.game_active = False
                top_score = max((v['score'] for v in self.scores.values()), default=0)
                winners = [v['name'] for v in self.scores.values() if v['score'] == top_score]
                winner_text = ", ".join(winners)
                return {
                    "response": self.build_text_message(f"انتهت اللعبة! الفائز: {winner_text} مع {top_score} نقاط"),
                    "points": points
                }

            return {
                "response": self.get_question(),
                "points": points,
                "next_question": True
            }

        return {
            "response": self.build_text_message("الكلمة غير صحيحة"),
            "points": 0
        }
