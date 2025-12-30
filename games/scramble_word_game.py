import random
from games.base_game import BaseGame

class ScrambleGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=1, theme='light'):
        super().__init__(line_bot_api, difficulty=difficulty, theme=theme)
        self.game_name = "ترتيب"

        # خمس مستويات صعوبة، كل مستوى كلمات أطول وأكثر تحديًا
        self.difficulty_levels = {
            1: [
                "قلم","باب","كتاب","وردة","شمس","قمر","نهر","بيت","نملة","سمكة",
                "حوت","نجمة","كرسي","سيارة","طاولة","نافذة","حديقة","شجرة","فراشة","شارع"
            ],
            2: [
                "مدرسة","مستشفى","جامعة","مكتبة","متحف","مطار","محطة","ملعب","مسبح","سوق",
                "مسجد","كنيسة","حديقة_الحيوان","حديقة_النبات","مقهى","مطعم","مخبز","جسر","طريق","ميدان"
            ],
            3: [
                "مكتبة_جامعية","مركز_تجاري","مستشفى_خاص","مسجد_جامع","كنيسة_قديمة",
                "نهر_الأردن","بحيرة_طبريا","جبل_المرتفعات","حديقة_الوطن","ساحة_الشهداء",
                "شارع_الرياض","ميدان_التحرير","جسر_الملك","برج_الحرية","قصر_الملك",
                "بيت_الشاعر","مدينة_الذهب","قرية_الزهور","واحة_النخيل","شمس_الصباح"
            ],
            4: [
                "قمر_الليل","نجمة_الصحراء","مطر_الربيع","ثلج_الشتاء","سحابة_السماء",
                "سمكة_النهر","حوت_المحيط","فراشة_الحديقة","نملة_الغابة","كرسي_الحديقة",
                "طاولة_المكتبة","قلم_الكتابة","كتاب_المدرسة","مدرسة_التعليم","سيارة_المدرسة",
                "طائرة_الرحلة","حديقة_الزهور","جبل_الشمس","شاطئ_البحر","وادي_النهر"
            ],
            5: [
                "مدينة_التاريخ","قرية_العراقة","مستشفى_المدينة","جامعة_العلم","مركز_البحث",
                "ساحة_الثقافة","جسر_الحضارة","برج_المجد","قصر_الأساطير","مكتبة_التراث",
                "متحف_الآثار","مطار_الدولي","محطة_القطار","ميدان_الشهداء","شارع_الذكرى",
                "حديقة_الوطن","نهر_الخير","بحيرة_الأمل","جبل_الشموخ","صحراء_النجوم"
            ]
        }

        self.used_words = []
        self.current_answer = ""
        self.current_question = 0
        self.answered_users = set()
        self.game_active = False
        self.current_level = difficulty  # مستوى الصعوبة الحالي
        self.supports_hint = True  # لدعم التلميح

    def scramble_word(self, word):
        letters = list(word)
        random.shuffle(letters)
        return " ".join(letters)

    def start_game(self):
        self.game_active = True
        self.current_question = 0
        self.answered_users.clear()
        return self.get_question()

    def get_question(self):
        # اختر الكلمة حسب المستوى الحالي
        level_words = [w for w in self.difficulty_levels[self.current_level] if w not in self.used_words]

        if not level_words:
            self.used_words = []
            level_words = self.difficulty_levels[self.current_level].copy()
            random.shuffle(level_words)

        word = random.choice(level_words)
        self.used_words.append(word)
        self.current_answer = word
        self.current_question += 1

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

        # التلميح
        if self.supports_hint and normalized == "لمح":
            first_char = self.current_answer[0]
            length = len(self.current_answer.replace("_", " "))  # حساب عدد الحروف بما فيها المسافات
            words = self.current_answer.split("_")
            hint = f"أول حرف: {first_char}, عدد الحروف: {length}, كلمة/كلمتين: {' '.join(words)}"
            return {"response": self.build_text_message(hint), "points": 0}

        # التحقق من الإجابة الصحيحة
        if normalized == self.normalize_text(self.current_answer):
            points = self.add_score(user_id, display_name, 1)
            self.answered_users.clear()

            # كل 5 أسئلة نرفع المستوى حتى 5
            if self.current_question % 5 == 0 and self.current_level < 5:
                self.current_level += 1

            return {
                "response": self.get_question(),
                "points": points,
                "next_question": True
            }

        return {
            "response": self.build_text_message("الكلمة غير صحيحة"),
            "points": 0
        }
