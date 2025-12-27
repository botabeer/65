import random
import time
from games.base_game import BaseGame

class GuessGame(BaseGame):
    def __init__(self, line_bot_api, theme="light"):
        super().__init__(line_bot_api, game_type="competitive", difficulty=1, theme=theme)
        self.game_name = "خمن"
        
        # مجموعة الأسئلة بدون مستويات مع حوالي 50 مثال
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
    
    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.withdrawn_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if normalized in ["ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)
        
        if user_id in self.answered_users:
            return None
        
        # أمر لمحة
        if normalized == "لمح":
            self.hints_used += 1
            if self.current_answer:
                sample = self.current_answer[0]
                hint_text = f"لمح: يبدأ بحرف '{sample[0]}' وعدد حروف الكلمة: {len(sample)}"
            else:
                hint_text = "لمح: لا يوجد كلمة حالياً"
            return {"response": self.build_text_message(hint_text), "points": 0}
        
        # أمر جاوب
        if normalized == "جاوب":
            if self.current_answer:
                answers = " أو ".join(self.current_answer)
                self.previous_answer = answers
            else:
                answers = "لا توجد إجابة"
            self.current_question += 1
            self.answered_users.clear()
            return {"response": self.build_text_message(f"الإجابة الصحيحة: {answers}"), "points": 0, "next_question": True}
        
        # التحقق من الإجابة الصحيحة
        for correct in self.current_answer:
            if self.normalize_text(correct) == normalized:
                self.answered_users.add(user_id)
                points = 1
                earned = self.add_score(user_id, display_name, points)
                
                self.previous_answer = user_answer.strip()
                self.current_question += 1
                self.answered_users.clear()
                self.hints_used = 0
                
                if self.current_question >= self.questions_count:
                    result = self.end_game()
                    result["points"] = earned
                    return result
                
                return {"response": self.get_question(), "points": earned, "next_question": True}
        
        return None
