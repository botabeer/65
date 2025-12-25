"""
Guess Game - لعبة تخمين منافسة مع مستويات صعوبة
"""
import random
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
                "المهن": {"م": ["معلم", "مهندس"], "ط": ["طبيب"], "م": ["محامي"]}
            }
        }
        
        self.items = self.items_by_difficulty.get(difficulty, self.items_by_difficulty[3])
        self.questions_list = []
        self.hints_used = 0
        
        for category, letters in self.items.items():
            for letter, words in letters.items():
                self.questions_list.append({
                    "category": category,
                    "letter": letter,
                    "answers": words
                })
        
        random.shuffle(self.questions_list)
    
    def get_question(self):
        """الحصول على السؤال"""
        self.round_start_time = time.time()
        q = self.questions_list[self.current_question % len(self.questions_list)]
        self.current_answer = q["answers"]
        
        return self.build_question_message(
            f"الفئة: {q['category']}",
            f"يبدا بحرف: {q['letter']}"
        )
    
    def check_answer(self, user_answer, user_id, display_name):
        """التحقق من الإجابة"""
        if not self.game_active:
            return None
        
        if user_id in self.withdrawn_users:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if normalized in ["انسحب", "انسحاب"]:
            return self.handle_withdrawal(user_id, display_name)
        
        if user_id in self.answered_users:
            return None
        
        if self.supports_hint and normalized == "لمح":
            self.hints_used += 1
            sample = self.current_answer[0] if self.current_answer else "كلمة"
            hint_text = f"يبدا بـ: {sample[0]}\nعدد الحروف: {len(sample)}"
            if self.hint_penalty > 0:
                hint_text += f"\n(سيتم خصم {self.hint_penalty} نقطة)"
            return {
                "response": self.build_text_message(hint_text),
                "points": 0
            }
        
        if self.supports_reveal and normalized == "جاوب":
            answers = " او ".join(self.current_answer)
            self.previous_question = f"الفئة: {self.questions_list[self.current_question]['category']}"
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
                
                self.previous_question = f"الفئة: {self.questions_list[self.current_question]['category']}"
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
