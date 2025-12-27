# games/fast_typing_game.py
import random
import time
from games.base_game import BaseGame
from linebot.v3.messaging import FlexMessage, FlexContainer

class FastTypingGame(BaseGame):
    def __init__(self, line_bot_api, difficulty=1, theme='light'):
        super().__init__(line_bot_api, game_type="competitive", theme=theme)
        self.game_name = "اسرع"
        self.questions_count = 5
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        self.withdrawn_users = set()
        self.round_start_time = None
        self.first_correct_answer = False
        self.supports_hint = False
        self.supports_reveal = False
        self.difficulty = difficulty  # كل مستوى يزيد الوقت المتاح

        # 50 مثال من أدعية وأذكار وحكم ومواعظ
        self.phrases = [
            "سبحان الله", "الحمد لله", "الله اكبر", "لا اله الا الله",
            "استغفر الله", "لا حول ولا قوة الا بالله", "بسم الله الرحمن الرحيم",
            "يارب", "اللهم صل على محمد", "توكلت على الله",
            "ما شاء الله", "بارك الله فيك", "جزاك الله خيرا",
            "التوكل على الله طمأنينة", "العقل زينة الانسان", "الصبر مفتاح الفرج",
            "العلم نور", "من جد وجد", "النية الصالحة طريق النجاح",
            "احسن للناس تكن لهم خيرا", "الدعاء سلاح المؤمن", "الوقت كالسيف",
            "التقوى خير زاد", "احذر الغيبة", "السعادة في الرضا",
            "العفو من شيم الكرام", "الصدق منجاة", "الحياء من الايمان",
            "من تواضع لله رفعه", "التعاون من شيم الاخيار", "الكلمة الطيبة صدقة",
            "العقلاء هم القلة", "لا تؤجل عمل اليوم الى الغد", "الحكمة ضالة المؤمن",
            "الرفق اساس التربية", "العلماء ورثة الانبياء", "النية تحكم العمل",
            "الدنيا فانية", "الصحة تاج على رؤوس الاصحاء", "الشكر يزيد النعم",
            "الاستغفار يفتح الابواب", "التسامح يلين القلوب", "المحبة سبب للسلام",
            "العبادة راحة للنفس", "العمل عبادة", "التواضع مفتاح القلوب",
            "العلم بالعمل يزيد", "الصلاة عمود الدين", "القراءة غذاء الروح",
            "الذكر يرفع الدرجات", "الاحسان الى الناس يزيد المحبة"
        ]
        self.used_phrases = []
        self.current_answer = None
        self.previous_question = None

    def start_game(self):
        self.game_active = True
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        self.withdrawn_users = set()
        self.first_correct_answer = False
        self.used_phrases = []
        return self.get_question()

    def get_question(self):
        target_words = min(self.current_question + 1, 5)
        available = [p for p in self.phrases if p not in self.used_phrases and len(p.split()) == target_words]
        if not available:
            available = [p for p in self.phrases if len(p.split()) == target_words]
        phrase = random.choice(available)
        self.used_phrases.append(phrase)
        self.current_answer = phrase
        self.round_start_time = time.time()
        self.first_correct_answer = False

        c = self.get_theme_colors()
        progress = int((self.current_question / self.questions_count) * 100)
        round_time = self.difficulty * 10

        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": self.game_name, "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
                    {"type": "text", "text": f"السؤال {self.current_question + 1} من {self.questions_count}", "size": "sm", "color": c["text2"], "align": "center", "margin": "sm"},
                    {"type": "box", "layout": "horizontal", "contents": [
                        {"type": "box", "layout": "vertical", "contents": [], "width": f"{progress}%", "height": "6px", "backgroundColor": "#2563EB", "cornerRadius": "3px"}
                    ], "height": "6px", "backgroundColor": c["border"], "cornerRadius": "3px", "margin": "sm"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": phrase, "size": "lg", "wrap": True, "color": c["text"], "align": "center", "weight": "bold", "margin": "lg"},
                    {"type": "text", "text": f"الوقت المتبقي: {round_time} ثانية", "size": "sm", "color": c["text2"], "align": "center", "margin": "md"}
                ],
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {"type": "button", "action": {"type": "message", "label": "ايقاف", "text": "ايقاف"}, "style": "secondary", "height": "sm", "color": c["primary"], "flex": 1}
                ],
                "spacing": "sm",
                "paddingAll": "12px",
                "backgroundColor": c["card"]
            }
        }
        return FlexMessage(alt_text=self.game_name, contents=FlexContainer.from_dict(bubble))

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active or user_id in self.withdrawn_users:
            return None

        normalized = self.normalize_text(user_answer)
        if normalized == "ايقاف":
            return self.handle_withdrawal(user_id, display_name)

        if self.first_correct_answer:
            return None

        elapsed = time.time() - self.round_start_time
        max_time = self.difficulty * 10
        if elapsed > max_time:
            self.previous_answer = "انتهى الوقت"
            self.current_question += 1
            self.answered_users.clear()
            if self.current_question >= self.questions_count:
                return self.end_game()
            return {"response": self.get_question(), "points": 0, "next_question": True}

        if user_answer.strip() == self.current_answer:
            self.first_correct_answer = True
            points = self.add_score(user_id, display_name, 1)
            self.previous_answer = user_answer.strip()
            self.current_question += 1
            self.answered_users.clear()
            if self.current_question >= self.questions_count:
                result = self.end_game()
                result["points"] = points
                return result
            return {"response": self.get_question(), "points": points, "next_question": True}

        return None
