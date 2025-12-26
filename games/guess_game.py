import random
import time
from games.base_game import BaseGame

class GuessGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=3, theme="light"):
        super().__init__(line_bot_api, game_type="competitive", difficulty=difficulty, theme=theme)
        self.game_name = "خمن"
        
        self.items_by_difficulty = {
            1: {
                "المطبخ": {"ق": ["قدر"], "م": ["ملعقة"], "س": ["سكين"], "ك": ["كوب"]},
                "الحيوانات": {"ق": ["قطة"], "ك": ["كلب"], "ح": ["حمار"]}
            },
            2: {
                "المطبخ": {"ق": ["قدر"], "م": ["ملعقة"], "س": ["سكين"], "ك": ["كوب"], "ص": ["صحن"]},
                "الحيوانات": {"ق": ["قطة"], "ك": ["كلب"], "ح": ["حمار"], "ف": ["فار"]},
                "الفواكه": {"ت": ["تفاح"], "م": ["موز"], "ع": ["عنب"]}
            },
            3: {
                "المطبخ": {"ق": ["قدر"], "م": ["ملعقة"], "س": ["سكين"], "ك": ["كوب"], "ص": ["صحن"], "ف": ["فرن"]},
                "غرفة النوم": {"س": ["سرير"], "و": ["وسادة"], "م": ["مراة"], "خ": ["خزانة"]},
                "المدرسة": {"ق": ["قلم"], "د": ["دفتر"], "ك": ["كتاب"], "م": ["مسطرة"]},
                "الفواكه": {"ت": ["تفاح"], "م": ["موز"], "ع": ["عنب"], "ب": ["برتقال"]},
                "الحيوانات": {"ق": ["قطة"], "ف": ["فيل"], "ا": ["اسد"], "ن": ["نمر"]}
            },
            4: {
                "المطبخ": {"ق": ["قدر", "قلاية"], "م": ["ملعقة", "مقلاة"], "س": ["سكين"], "ك": ["كوب"], "ف": ["فرن", "فنجان"]},
                "غرفة النوم": {"س": ["سرير"], "و": ["وسادة"], "م": ["مراة", "مخدة"], "خ": ["خزانة"]},
                "المدرسة": {"ق": ["قلم"], "د": ["دفتر"], "ك": ["كتاب"], "م": ["مسطرة", "ممحاة"], "ح": ["حقيبة"]},
                "الفواكه": {"ت": ["تفاح", "توت"], "م": ["موز", "مشمش"], "ع": ["عنب"], "ب": ["برتقال"]},
                "الحيوانات": {"ق": ["قطة", "قرد"], "ف": ["فيل", "فار"], "ا": ["اسد"], "ن": ["نمر", "نعامة"]},
                "البلاد": {"س": ["سعودية", "سوريا"], "م": ["مصر"], "ع": ["عمان"]}
            },
            5: {
                "المطبخ": {"ق": ["قدر", "قلاية"], "م": ["ملعقة", "مقلاة", "مغرفة"], "س": ["سكين"], "ك": ["كوب"], "ف": ["فرن", "فنجان"], "ط": ["طنجرة"]},
                "غرفة النوم": {"س": ["سرير"], "و": ["وسادة"], "م": ["مراة", "مخدة"], "خ": ["خزانة"], "ل": ["لحاف"]},
                "المدرسة": {"ق": ["قلم"], "د": ["دفتر"], "ك": ["كتاب"], "م": ["مسطرة", "ممحاة"], "ح": ["حقيبة"], "ب": ["براية"]},
                "الفواكه": {"ت": ["تفاح", "توت"], "م": ["موز", "مشمش", "مانجو"], "ع": ["عنب"], "ب": ["برتقال"], "ر": ["رمان"]},
                "الحيوانات": {"ق": ["قطة", "قرد"], "ف": ["فيل", "فار", "فهد"], "ا": ["اسد", "ارنب"], "ن": ["نمر", "نعامة"], "ز": ["زرافة"]},
                "البلاد": {"س": ["سعودية", "سوريا", "سودان"], "م": ["مصر", "مغرب"], "ع": ["عمان", "عراق"], "ي": ["يمن"]},
                "المهن": {"م": ["معلم", "مهندس"], "ط": ["طبيب"], "محامي": ["محامي"]}
            }
        }
        
        self.items = self.items_by_difficulty.get(difficulty, self.items_by_difficulty[3])
        self.questions_pool = []
        self.hints_used = 0
        
        # إنشاء مجموعة الأسئلة
        for category, letters in self.items.items():
            for letter, words in letters.items():
                question_id = f"{category}_{letter}"
                self.questions_pool.append({
                    "id": question_id,
                    "category": category,
                    "letter": letter,
                    "answers": words
                })
        
        random.shuffle(self.questions_pool)
    
    def get_question(self):
        self.round_start_time = time.time()
        
        # البحث عن سؤال لم يتم استخدامه
        available_questions = [q for q in self.questions_pool if q["id"] not in self.used_questions]
        
        # إذا انتهت جميع الأسئلة، إعادة تعيين
        if not available_questions:
            self.used_questions.clear()
            self.all_questions_used = True
            available_questions = self.questions_pool.copy()
            random.shuffle(available_questions)
        
        q = available_questions[0]
        self.used_questions.add(q["id"])
        
        self.current_answer = q["answers"]
        
        return self.build_question_message(
            f"الفئة: {q['category']}",
            f"يبدأ بحرف: {q['letter']}"
        )
    
    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active:
            return None
        
        if user_id in self.withdrawn_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if normalized in ["ايقاف", "ايقاف"]:
            return self.handle_withdrawal(user_id, display_name)
        
        if user_id in self.answered_users:
            return None
        
        if self.supports_hint and normalized == "لمح":
            self.hints_used += 1
            sample = self.current_answer[0] if self.current_answer else "كلمة"
            hint_text = f"يبدأ بـ: {sample[0]}\nعدد الحروف: {len(sample)}"
            if self.hint_penalty > 0:
                hint_text += f"\nسيتم خصم {self.hint_penalty} نقطة"
            return {
                "response": self.build_text_message(hint_text),
                "points": 0
            }
        
        if self.supports_reveal and normalized == "جاوب":
            answers = " أو ".join(self.current_answer)
            self.previous_answer = answers
            self.current_question += 1
            self.answered_users.clear()
            
            if self.current_question >= self.questions_count:
                return self.end_game()
            
            return {
                "response": self.get_question(),
                "points": 0,
                "next_question": True
            }
        
        for correct in self.current_answer:
            if self.normalize_text(correct) == normalized:
                self.answered_users.add(user_id)
                points = 1 - (self.hints_used * self.hint_penalty)
                points = max(0, points)
                self.hints_used = 0
                
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
