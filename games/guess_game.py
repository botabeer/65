import random
import time
from games.base_game import BaseGame

class GuessGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme="light"):
        super().__init__(line_bot_api, game_type="competitive", difficulty=difficulty, theme=theme)
        self.game_name = "خمن"
        
        self.items_by_level = {
            1: {
                "المطبخ": {"ق": ["قدر"], "م": ["ملعقة"], "ك": ["كوب"]},
                "الحيوانات": {"ق": ["قطة"], "ك": ["كلب"]}
            },
            2: {
                "المطبخ": {"ق": ["قدر"], "م": ["ملعقة"], "س": ["سكين"], "ك": ["كوب"]},
                "الحيوانات": {"ق": ["قطة"], "ك": ["كلب"], "ح": ["حمار"]},
                "الفواكه": {"ت": ["تفاح"], "م": ["موز"]}
            },
            3: {
                "المطبخ": {"ق": ["قدر"], "م": ["ملعقة"], "س": ["سكين"], "ك": ["كوب"], "ص": ["صحن"]},
                "غرفة النوم": {"س": ["سرير"], "و": ["وسادة"], "م": ["مراة"]},
                "الفواكه": {"ت": ["تفاح"], "م": ["موز"], "ع": ["عنب"]},
                "الحيوانات": {"ق": ["قطة"], "ف": ["فيل"], "ا": ["اسد"]}
            },
            4: {
                "المطبخ": {"ق": ["قدر", "قلاية"], "م": ["ملعقة", "مقلاة"], "س": ["سكين"]},
                "غرفة النوم": {"س": ["سرير"], "و": ["وسادة"], "م": ["مراة", "مخدة"]},
                "المدرسة": {"ق": ["قلم"], "د": ["دفتر"], "ك": ["كتاب"], "م": ["مسطرة"]},
                "الفواكه": {"ت": ["تفاح", "توت"], "م": ["موز"], "ع": ["عنب"], "ب": ["برتقال"]},
                "البلاد": {"س": ["سعودية"], "م": ["مصر"], "ع": ["عمان"]}
            },
            5: {
                "المطبخ": {"ق": ["قدر", "قلاية"], "م": ["ملعقة", "مقلاة", "مغرفة"], "ط": ["طنجرة"]},
                "غرفة النوم": {"س": ["سرير"], "و": ["وسادة"], "م": ["مراة", "مخدة"], "ل": ["لحاف"]},
                "المدرسة": {"ق": ["قلم"], "د": ["دفتر"], "ك": ["كتاب"], "م": ["مسطرة", "ممحاة"], "ب": ["براية"]},
                "الفواكه": {"ت": ["تفاح", "توت"], "م": ["موز", "مشمش"], "ر": ["رمان"]},
                "البلاد": {"س": ["سعودية", "سوريا"], "م": ["مصر", "مغرب"], "ع": ["عمان"], "ي": ["يمن"]},
                "المهن": {"م": ["معلم", "مهندس"], "ط": ["طبيب"]}
            }
        }
        
        self.questions_pool = []
        self.hints_used = 0
        self._build_questions_pool()
    
    def _build_questions_pool(self):
        for level in range(1, 6):
            items = self.items_by_level.get(level, self.items_by_level[3])
            for category, letters in items.items():
                for letter, words in letters.items():
                    self.questions_pool.append({
                        "id": f"{level}_{category}_{letter}",
                        "level": level,
                        "category": category,
                        "letter": letter,
                        "answers": words
                    })
        random.shuffle(self.questions_pool)
    
    def get_question(self):
        self.round_start_time = time.time()
        current_level = 3
        
        available = [q for q in self.questions_pool 
                    if q["id"] not in self.used_questions and q["level"] == current_level]
        
        if not available:
            available = [q for q in self.questions_pool 
                        if q["id"] not in self.used_questions and 
                        abs(q["level"] - current_level) <= 1]
        
        if not available:
            self.used_questions.clear()
            available = [q for q in self.questions_pool if q["level"] == current_level]
        
        if not available:
            available = self.questions_pool.copy()
        
        q = random.choice(available)
        self.used_questions.add(q["id"])
        self.current_answer = q["answers"]
        
        return self.build_question_message(f"الفئة: {q['category']}", f"يبدأ بحرف: {q['letter']}")
    
    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.withdrawn_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if normalized in ["ايقاف", "ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)
        
        if user_id in self.answered_users:
            return None
        
        if self.supports_hint and normalized == "لمح":
            self.hints_used += 1
            sample = self.current_answer[0] if self.current_answer else "كلمة"
            hint_text = f"يبدأ بحرف: {sample[0]}\nعدد الحروف: {len(sample)}"
            return {"response": self.build_text_message(hint_text), "points": 0}
        
        if self.supports_reveal and normalized == "جاوب":
            answers = " او ".join(self.current_answer)
            self.previous_answer = answers
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                return self.end_game()
            
            return {"response": self.get_question(), "points": 0, "next_question": True}
        
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
