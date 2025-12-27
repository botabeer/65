import random
import time
from games.base_game import BaseGame

class GuessGame(BaseGame):
    def __init__(self, line_bot_api, theme="light"):
        super().__init__(line_bot_api, theme=theme, game_type="competitive")
        self.game_name = "خمن"

        # مجموعة الأسئلة بدون مستويات، حوالي 50 مثال
        self.items = {
            "المطبخ": {
                "ق": ["قدر", "قلاية"],
                "م": ["ملعقة", "مقلاة", "مغرفة"],
                "س": ["سكين", "صحن"],
                "ك": ["كوب", "كنكة"],
                "ط": ["طنجرة"]
            },
            "الحيوانات": {
                "ق": ["قطة"],
                "ك": ["كلب", "كنغر"],
                "ح": ["حمار", "حصان"],
                "ف": ["فيل"],
                "ا": ["أسد", "أرنب"],
                "ن": ["نمر"]
            },
            "الفواكه": {
                "ت": ["تفاح", "توت"],
                "م": ["موز", "مشمش"],
                "ع": ["عنب"],
                "ب": ["برتقال", "بطيخ"],
                "ر": ["رمان"],
                "ك": ["كرز"]
            },
            "غرفة النوم": {
                "س": ["سرير", "ستارة"],
                "و": ["وسادة"],
                "م": ["مراة", "مخدة"],
                "ل": ["لحاف"]
            },
            "المدرسة": {
                "ق": ["قلم", "قلم رصاص"],
                "د": ["دفتر"],
                "ك": ["كتاب", "كمبيوتر"],
                "م": ["مسطرة", "ممحاة"],
                "ب": ["براية"]
            },
            "البلاد": {
                "س": ["سعودية", "سوريا"],
                "م": ["مصر", "مغرب"],
                "ع": ["عمان"],
                "ي": ["اليمن", "يابان"]
            },
            "المهن": {
                "م": ["معلم", "مهندس", "مزارع", "محامي"],
                "ط": ["طبيب", "طيار"],
                "ف": ["فنان"]
            }
        }

        self.questions_pool = []
        self.hints_used = 0
        self.used_questions = set()
        self._build_questions_pool()

    def _build_questions_pool(self):
        for category, letters in self.items.items():
            for letter, words in letters.items():
                self.questions_pool.append({
                    "id": f"{category}_{letter}",
                    "category": category,
                    "letter": letter,
                    "answers": words
                })
        random.shuffle(self.questions_pool)

    def get_question(self):
        self.round_start_time = time.time()
        available = [q for q in self.questions_pool if q["id"] not in self.used_questions]
        if not available:
            self.used_questions.clear()
            available = self.questions_pool.copy()
            random.shuffle(available)

        q = random.choice(available)
        self.used_questions.add(q["id"])
        self.current_answer = q["answers"]

        return self.build_question_message(f"الفئة: {q['category']}", f"يبدأ بحرف: {q['letter']}")

    def validate_answer(self, normalized, user_id, display_name):
        correct_answers = self.current_answer if isinstance(self.current_answer, list) else [self.current_answer]
        for correct in correct_answers:
            if self.normalize_text(str(correct)) == normalized:
                return self.handle_correct_answer(user_id, display_name)
        return None
