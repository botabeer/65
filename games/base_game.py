from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import re
import time

class BaseGame:
    """الفئة الأساسية لجميع الألعاب"""
    
    THEMES = {
        "light": {
            "primary": "#2563EB",
            "success": "#10B981",
            "warning": "#F59E0B",
            "error": "#EF4444",
            "text": "#1F2937",
            "text2": "#6B7280",
            "bg": "#F9FAFB",
            "card": "#FFFFFF",
            "border": "#E5E7EB"
        },
        "dark": {
            "primary": "#3B82F6",
            "success": "#34D399",
            "warning": "#FBBF24",
            "error": "#F87171",
            "text": "#F9FAFB",
            "text2": "#D1D5DB",
            "bg": "#1F2937",
            "card": "#374151",
            "border": "#4B5563"
        }
    }
    
    def __init__(self, line_bot_api, questions_count=5):
        self.line_bot_api = line_bot_api
        self.questions_count = questions_count
        self.current_question = 0
        self.game_active = False
        self.game_name = "لعبة"
        self.scores = {}
        self.answered_users = set()
        self.current_answer = None
        self.previous_question = None
        self.previous_answer = None
        self.start_time = None
        self.supports_hint = True
        self.supports_reveal = True
    
    def normalize_text(self, text):
        """تطبيع النص العربي"""
        if not text:
            return ""
        text = text.strip().lower()
        trans = str.maketrans({
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
            'ؤ': 'و', 'ئ': 'ي', 'ء': '',
            'ة': 'ه', 'ى': 'ي'
        })
        text = text.translate(trans)
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        return re.sub(r'\s+', ' ', text).strip()
    
    def add_score(self, user_id, display_name, points=1):
        """إضافة نقاط للاعب"""
        if user_id not in self.scores:
            self.scores[user_id] = {'name': display_name, 'score': 0}
        self.scores[user_id]['score'] += points
        return points
    
    def get_theme_colors(self, theme='light'):
        """الحصول على ألوان الثيم"""
        return self.THEMES.get(theme, self.THEMES['light'])
    
    def build_question_message(self, question_text, subtitle=None):
        """بناء رسالة السؤال"""
        c = self.get_theme_colors()
        contents = [
            {"type": "text", "text": self.game_name, "size": "xl", "weight": "bold", 
             "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "lg", "color": c["border"]},
        ]
        
        if self.previous_answer:
            contents.append({
                "type": "text",
                "text": f"الإجابة السابقة: {self.previous_answer}",
                "size": "xs",
                "color": c["text2"],
                "align": "center",
                "margin": "md"
            })
        
        contents.extend([
            {"type": "text", "text": f"السؤال {self.current_question + 1}/{self.questions_count}",
             "size": "sm", "color": c["text2"], "align": "center", "margin": "md"},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {"type": "text", "text": question_text, "size": "md", "wrap": True,
             "color": c["text"], "align": "center", "margin": "lg"}
        ])
        
        if subtitle:
            contents.append({
                "type": "text", "text": subtitle, "size": "xs",
                "color": c["text2"], "align": "center", "margin": "sm"
            })
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            }
        }
        
        return FlexMessage(alt_text=self.game_name, contents=FlexContainer.from_dict(bubble))
    
    def build_text_message(self, text):
        """بناء رسالة نصية بسيطة"""
        return TextMessage(text=text)
    
    def start_game(self):
        """بدء اللعبة"""
        self.game_active = True
        self.current_question = 0
        self.scores = {}
        self.answered_users = set()
        return self.get_question()
    
    def get_question(self):
        """الحصول على السؤال - يجب تنفيذها في الفئات الفرعية"""
        raise NotImplementedError("يجب تنفيذ get_question في الفئة الفرعية")
    
    def check_answer(self, user_answer, user_id, display_name):
        """التحقق من الإجابة - يجب تنفيذها في الفئات الفرعية"""
        raise NotImplementedError("يجب تنفيذ check_answer في الفئة الفرعية")
    
    def end_game(self):
        """إنهاء اللعبة"""
        self.game_active = False
        if not self.scores:
            return {
                "game_over": True,
                "points": 0,
                "message": "انتهت اللعبة\nلم يسجل أحد نقاطاً",
                "response": self.build_text_message("انتهت اللعبة")
            }
        
        sorted_players = sorted(
            self.scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        winner = sorted_players[0][1]
        result_text = f"🏆 انتهت اللعبة\n\nالفائز: {winner['name']}\nالنقاط: {winner['score']}"
        
        if len(sorted_players) > 1:
            result_text += "\n\n📊 الترتيب:\n"
            for i, (uid, player) in enumerate(sorted_players[:5], 1):
                result_text += f"{i}. {player['name']} - {player['score']} نقطة\n"
        
        return {
            "game_over": True,
            "points": winner['score'],
            "won": True,
            "message": result_text,
            "response": self.build_text_message(result_text)
        }
    
    def _create_flex_with_buttons(self, alt_text, bubble):
        """إنشاء Flex Message مع أزرار"""
        return FlexMessage(alt_text=alt_text, contents=FlexContainer.from_dict(bubble))
    
    def _create_text_message(self, text):
        """إنشاء رسالة نصية"""
        return TextMessage(text=text)
