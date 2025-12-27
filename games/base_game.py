from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import re, time
from typing import Dict, Any
from abc import ABC, abstractmethod

class BaseGame(ABC):
    THEMES = {
        "light": {
            "primary": "#1A1A1A", "text": "#2D2D2D", "text2": "#6B7280",
            "bg": "#FFFFFF", "card": "#F9FAFB", "border": "#E5E7EB",
            "button": "#F5F5F5", "success": "#2563EB"
        },
        "dark": {
            "primary": "#F9FAFB", "text": "#E5E7EB", "text2": "#9CA3AF",
            "bg": "#111827", "card": "#1F2937", "border": "#374151",
            "button": "#F5F5F5", "success": "#60A5FA"
        }
    }

    def __init__(self, line_bot_api, theme="light", game_type="competitive"):
        self.line_bot_api = line_bot_api
        self.theme = theme
        self.game_type = game_type
        self.game_name = "لعبة"
        self.questions_count = 5
        self.current_question = 0
        self.game_active = False
        self.scores = {}
        self.answered_users = set()
        self.withdrawn_users = set()
        self.current_answer = None
        self.previous_answer = None
        self.start_time = None
        self.supports_hint = True
        self.supports_reveal = True

    def normalize_text(self, text):
        if not text: return ""
        text = str(text).strip().lower()
        trans = str.maketrans({'أ':'ا','إ':'ا','آ':'ا','ٱ':'ا','ؤ':'و','ئ':'ي','ء':'','ة':'ه','ى':'ي'})
        text = text.translate(trans)
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    def add_score(self, user_id, display_name):
        if user_id not in self.scores:
            self.scores[user_id] = {'name': display_name, 'score': 0}
        self.scores[user_id]['score'] += 1

    def get_theme_colors(self):
        return self.THEMES.get(self.theme, self.THEMES['light'])

    # -------------------- بناء السؤال -------------------- #
    def build_question_message_pro(self, question_text):
        c = self.get_theme_colors()
        progress = int((self.current_question / self.questions_count) * 100)
        contents = [
            {"type": "text", "text": self.game_name, "size": "xl",
             "weight": "bold", "align": "center", "color": c["primary"]},
            {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"السؤال {self.current_question + 1} من {self.questions_count}",
                     "size": "xs", "color": c["text2"], "align": "center", "margin": "sm"},
                    {"type": "box", "layout": "horizontal",
                     "contents": [{"type": "box", "layout": "vertical", "contents": [],
                                   "width": f"{progress}%", "height": "6px",
                                   "backgroundColor": c["success"], "cornerRadius": "3px"}],
                     "height": "6px", "backgroundColor": c["border"], "cornerRadius": "3px", "margin": "xs"}
                ], "margin": "md"
            },
            {"type": "text", "text": question_text, "size": "lg", "wrap": True,
             "color": c["text"], "align": "center", "margin": "lg", "weight": "bold"}
        ]
        footer_buttons = []
        if self.supports_hint:
            footer_buttons.append({"type":"button","action":{"type":"message","label":"لمح","text":"لمح"},
                                   "style":"secondary","height":"sm","color":c["button"],"flex":1})
        if self.supports_reveal:
            footer_buttons.append({"type":"button","action":{"type":"message","label":"جاوب","text":"جاوب"},
                                   "style":"secondary","height":"sm","color":c["button"],"flex":1})
        footer_buttons.append({"type":"button","action":{"type":"message","label":"ايقاف","text":"ايقاف"},
                               "style":"secondary","height":"sm","color":c["button"],"flex":1})
        bubble = {"type":"bubble","size":"mega",
                  "body":{"type":"box","layout":"vertical","contents":contents,"paddingAll":"20px","backgroundColor":c["bg"]},
                  "footer":{"type":"box","layout":"horizontal","contents":footer_buttons,"spacing":"sm","paddingAll":"12px","backgroundColor":c["card"]}}
        return FlexMessage(alt_text=self.game_name, contents=FlexContainer.from_dict(bubble))

    def build_text_message(self, text):
        return TextMessage(text=text)

    # -------------------- إدارة اللعبة -------------------- #
    def start_game(self):
        self.game_active = True
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        self.withdrawn_users = set()
        self.start_time = time.time()
        return self.get_question()

    @abstractmethod
    def get_question(self):
        pass

    @abstractmethod
    def check_answer(self, user_answer):
        """ترجع قائمة الاجابات الصحيحة"""
        pass

    # -------------------- معالجة الرسائل -------------------- #
    def handle_message(self, user_id, display_name, text):
        if not self.game_active:
            return None
        normalized = self.normalize_text(text)

        # ايقاف اللاعب
        if normalized == "ايقاف":
            self.withdrawn_users.add(user_id)
            if user_id in self.scores: del self.scores[user_id]
            return {"response": self.build_text_message(f"{display_name} انسحب من اللعبة"), "points":0, "withdrawn":True}

        # طلب تلميح
        if normalized == "لمح":
            if not self.current_answer: return None
            hint = f"الحرف الأول: {self.current_answer[0]} | عدد الحروف: {len(self.current_answer)}"
            return {"response": self.build_text_message(hint), "points":0}

        # كشف الإجابة
        if normalized == "جاوب":
            if not self.current_answer: return None
            answer_text = f"الإجابة الصحيحة: {self.current_answer}"
            self.current_question += 1
            if self.current_question >= self.questions_count:
                return self.end_game()
            return {"response": self.build_text_message(answer_text), "next": self.get_question()}

        # التحقق من الإجابة الصحيحة (أول من يجاوب)
        correct_answers = self.check_answer(text)
        if normalized in [self.normalize_text(a) for a in correct_answers] and user_id not in self.answered_users:
            self.add_score(user_id, display_name)
            self.answered_users.add(user_id)
            self.previous_answer = self.current_answer
            self.current_question += 1
            self.answered_users.clear()
            if self.current_question >= self.questions_count:
                return self.end_game()
            return self.get_question()

        return None

    # -------------------- إنهاء اللعبة -------------------- #
    def end_game(self):
        self.game_active = False
        c = self.get_theme_colors()
        if not self.scores:
            return {"response": self.build_text_message("انتهت اللعبة ولم يسجل أحد نقاط")}
        sorted_players = sorted(self.scores.items(), key=lambda x: -x[1]['score'])
        winner = sorted_players[0][1]
        return {"response": self.build_text_message(f" الفائز: {winner['name']} | النقاط: {winner['score']}")}
