"""
Compatibility Game - لعبة حساب التوافق (ترفيهية بدون نقاط)
"""
import re
from games.base_game import BaseGame

class CompatibilityGame(BaseGame):
    def __init__(self, line_bot_api, theme="light"):
        super().__init__(line_bot_api, questions_count=1, game_type="entertainment", theme=theme)
        self.game_name = "توافق"
        
        self.supports_hint = False
        self.supports_reveal = False
        self.supports_difficulty = False
        self.show_progress = False
    
    def is_valid_text(self, text):
        """التحقق من أن النص أسماء فقط"""
        return not re.search(r"[@#0-9A-Za-z!$%^&*()_+=\[\]{};:'\"\\|,.<>/?~`]", text)
    
    def parse_names(self, text):
        """استخراج الاسمين من النص"""
        text = ' '.join(text.split())
        
        if ' و ' in text:
            parts = text.split(' و ', 1)
            return (parts[0].strip(), parts[1].strip())
        
        words = text.split()
        if 'و' in words:
            idx = words.index('و')
            return (' '.join(words[:idx]).strip(), ' '.join(words[idx+1:]).strip())
        
        return (None, None)
    
    def calculate_compatibility(self, name1, name2):
        """حساب نسبة التوافق بطريقة ترفيهية"""
        n1 = self.normalize_text(name1)
        n2 = self.normalize_text(name2)
        
        combined = ''.join(sorted([n1, n2]))
        seed = sum(ord(c) * (i + 1) for i, c in enumerate(combined))
        
        percentage = (seed % 81) + 20
        return percentage
    
    def get_compatibility_message(self, percentage):
        """الحصول على رسالة التوافق"""
        if percentage >= 90:
            return "توافق ممتاز جدا"
        elif percentage >= 75:
            return "توافق عالي جدا"
        elif percentage >= 60:
            return "توافق جيد"
        elif percentage >= 45:
            return "توافق متوسط"
        elif percentage >= 30:
            return "توافق ضعيف"
        else:
            return "توافق منخفض جدا"
    
    def get_compatibility_color(self, percentage):
        """الحصول على لون حسب النسبة"""
        c = self.get_theme_colors()
        if percentage >= 75:
            return c["success"]
        elif percentage >= 60:
            return c["info"]
        elif percentage >= 45:
            return c["warning"]
        else:
            return c["error"]
    
    def start_game(self):
        """بدء اللعبة"""
        self.game_active = True
        return self.get_question()
    
    def get_question(self):
        """الحصول على السؤال"""
        c = self.get_theme_colors()
        
        contents = [
            {
                "type": "text",
                "text": self.game_name,
                "size": "xl",
                "weight": "bold",
                "color": c["primary"],
                "align": "center"
            },
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "text",
                "text": "احسب نسبة التوافق",
                "size": "md",
                "color": c["text"],
                "align": "center",
                "margin": "lg"
            },
            {
                "type": "text",
                "text": "ادخل اسمين بينهما حرف (و)",
                "size": "sm",
                "color": c["text2"],
                "align": "center",
                "wrap": True,
                "margin": "sm"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "مثال: اسم و اسم",
                        "size": "xs",
                        "color": c["text3"],
                        "align": "center"
                    }
                ],
                "backgroundColor": c["card"],
                "cornerRadius": "8px",
                "paddingAll": "12px",
                "margin": "md"
            },
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "text",
                "text": "ملاحظة: هذه اللعبة للترفيه فقط",
                "size": "xxs",
                "color": c["text3"],
                "align": "center",
                "margin": "md"
            }
        ]
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "ايقاف", "text": "ايقاف"},
                        "style": "secondary",
                        "height": "sm",
                        "color": c["error"]
                    }
                ],
                "paddingAll": "12px",
                "backgroundColor": c["card"]
            }
        }
        
        return self._create_flex_with_buttons("توافق", bubble)
    
    def check_answer(self, user_answer, user_id=None, display_name=None):
        """التحقق من الإجابة"""
        if not self.game_active:
            return None
        
        normalized = self.normalize_text(user_answer)
        
        if normalized in ["ايقاف", "انسحب"]:
            self.game_active = False
            return {
                "response": self.build_text_message("تم ايقاف اللعبة"),
                "points": 0,
                "game_over": True
            }
        
        name1, name2 = self.parse_names(user_answer)
        
        if not name1 or not name2:
            return {
                "response": self.build_text_message("الصيغة غير صحيحة\nاكتب: اسم و اسم"),
                "points": 0
            }
        
        if not self.is_valid_text(name1) or not self.is_valid_text(name2):
            return {
                "response": self.build_text_message("غير مسموح بالرموز او الارقام\nاستخدم اسماء عربية فقط"),
                "points": 0
            }
        
        percentage = self.calculate_compatibility(name1, name2)
        message_text = self.get_compatibility_message(percentage)
        color = self.get_compatibility_color(percentage)
        
        c = self.get_theme_colors()
        
        result_bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "نتيجة التوافق",
                        "size": "xl",
                        "weight": "bold",
                        "color": c["primary"],
                        "align": "center"
                    },
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": name1,
                                "size": "lg",
                                "color": c["text"],
                                "align": "center",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": "و",
                                "size": "sm",
                                "color": c["text2"],
                                "align": "center",
                                "margin": "sm"
                            },
                            {
                                "type": "text",
                                "text": name2,
                                "size": "lg",
                                "color": c["text"],
                                "align": "center",
                                "weight": "bold",
                                "margin": "sm"
                            }
                        ],
                        "backgroundColor": c["card"],
                        "cornerRadius": "12px",
                        "paddingAll": "16px",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"{percentage}%",
                                "size": "xxl",
                                "weight": "bold",
                                "color": color,
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": message_text,
                                "size": "md",
                                "color": c["text2"],
                                "align": "center",
                                "margin": "sm"
                            }
                        ],
                        "margin": "lg"
                    },
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {
                        "type": "text",
                        "text": f"ملاحظة: نفس النتيجة لو كتبت\n{name2} و {name1}",
                        "size": "xxs",
                        "color": c["text3"],
                        "align": "center",
                        "wrap": True,
                        "margin": "md"
                    }
                ],
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "اعادة", "text": "توافق"},
                        "style": "primary",
                        "height": "sm",
                        "color": c["primary"]
                    },
                    {
                        "type": "button",
                        "action": {"type": "message", "label": "ايقاف", "text": "ايقاف"},
                        "style": "secondary",
                        "height": "sm",
                        "color": c["error"]
                    }
                ],
                "spacing": "sm",
                "paddingAll": "12px",
                "backgroundColor": c["card"]
            }
        }
        
        self.game_active = False
        
        return {
            "response": self._create_flex_with_buttons("نتيجة التوافق", result_bubble),
            "points": 0,
            "game_over": True
        }
    
    def _create_flex_with_buttons(self, alt_text, bubble):
        """إنشاء Flex Message"""
        from linebot.v3.messaging import FlexMessage, FlexContainer
        return FlexMessage(alt_text=alt_text, contents=FlexContainer.from_dict(bubble))
