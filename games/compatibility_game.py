import re
from games.base_game import BaseGame
from linebot.v3.messaging import FlexMessage, FlexContainer, TextMessage

class CompatibilityGame(BaseGame):
    def __init__(self, line_bot_api, theme="light"):
        super().__init__(line_bot_api, theme=theme)
        self.game_name = "توافق"
        self.supports_hint = False
        self.supports_reveal = False
        self.questions_count = 1
        self.game_active = False

    def is_valid_text(self, text):
        return not re.search(r"[@#0-9A-Za-z!$%^&*()_+=\[\]{};:'\"\\|,.<>/?~`]", text)

    def parse_names(self, text):
        text = ' '.join(text.split())
        if ' و ' in text:
            parts = text.split(' و ', 1)
            return parts[0].strip(), parts[1].strip()
        if 'و' in text:
            parts = text.split('و', 1)
            return parts[0].strip(), parts[1].strip()
        return None, None

    def calculate_compatibility(self, name1, name2):
        n1 = self.normalize_text(name1)
        n2 = self.normalize_text(name2)
        combined = ''.join(sorted([n1, n2]))
        seed = sum(ord(c) * (i + 1) for i, c in enumerate(combined))
        return (seed % 81) + 20

    def get_message_text(self, percentage):
        if percentage >= 90: return "توافق ممتاز جدا"
        if percentage >= 75: return "توافق عالي جدا"
        if percentage >= 60: return "توافق جيد"
        if percentage >= 45: return "توافق متوسط"
        if percentage >= 30: return "توافق ضعيف"
        return "توافق منخفض جدا"

    def get_message_color(self, percentage):
        c = self.get_theme_colors()
        if percentage >= 75: return c["success"]
        if percentage >= 60: return c["primary"]
        if percentage >= 45: return c["text2"]
        return c["text3"]

    def start_game(self):
        self.game_active = True
        return self.get_question()

    def get_question(self):
        c = self.get_theme_colors()
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "backgroundColor": c["bg"],
                "contents": [
                    {
                        "type": "text",
                        "text": self.game_name,
                        "size": "xl",
                        "weight": "bold",
                        "align": "center",
                        "color": c["primary"]
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": c["border"]
                    },
                    {
                        "type": "text",
                        "text": "احسب نسبة التوافق بين شخصين",
                        "size": "md",
                        "color": c["text"],
                        "align": "center",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "ادخل اسمين بينهما 'و'",
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
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": c["border"]
                    },
                    {
                        "type": "text",
                        "text": "ملاحظة: اللعبة للترفيه فقط",
                        "size": "xxs",
                        "color": c["text3"],
                        "align": "center",
                        "margin": "md"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "12px",
                "backgroundColor": c["card"],
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "ايقاف",
                            "text": "ايقاف"
                        },
                        "style": "secondary",
                        "height": "sm",
                        "color": self.BUTTON_COLOR
                    }
                ]
            }
        }
        return FlexMessage(alt_text="توافق", contents=FlexContainer.from_dict(bubble))

    def check_answer(self, user_answer, user_id, display_name):
        if not self.game_active:
            return None

        normalized = self.normalize_text(user_answer)
        if normalized == "ايقاف":
            self.game_active = False
            return {
                "response": TextMessage(text="تم ايقاف اللعبة"),
                "points": 0,
                "game_over": True
            }

        name1, name2 = self.parse_names(user_answer)
        if not name1 or not name2:
            return {
                "response": TextMessage(text="الصيغة غير صحيحة\nاكتب: اسم و اسم"),
                "points": 0
            }

        if not self.is_valid_text(name1) or not self.is_valid_text(name2):
            return {
                "response": TextMessage(text="غير مسموح بالرموز او الارقام\nاستخدم اسماء عربية فقط"),
                "points": 0
            }

        percentage = self.calculate_compatibility(name1, name2)
        message_text = self.get_message_text(percentage)
        color = self.get_message_color(percentage)
        c = self.get_theme_colors()

        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "backgroundColor": c["bg"],
                "contents": [
                    {
                        "type": "text",
                        "text": "نتيجة التوافق",
                        "size": "xl",
                        "weight": "bold",
                        "color": c["primary"],
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": c["border"]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "lg",
                        "backgroundColor": c["card"],
                        "cornerRadius": "12px",
                        "paddingAll": "16px",
                        "spacing": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": name1,
                                "size": "lg",
                                "color": c["text"],
                                "align": "center",
                                "weight": "bold",
                                "flex": 3
                            },
                            {
                                "type": "text",
                                "text": "و",
                                "size": "md",
                                "color": c["text2"],
                                "align": "center",
                                "flex": 1
                            },
                            {
                                "type": "text",
                                "text": name2,
                                "size": "lg",
                                "color": c["text"],
                                "align": "center",
                                "weight": "bold",
                                "flex": 3
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"{percentage}% - {message_text}",
                                "size": "md",
                                "weight": "bold",
                                "color": color,
                                "align": "center"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "sm",
                                "height": "8px",
                                "backgroundColor": c["border"],
                                "cornerRadius": "4px",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "backgroundColor": color,
                                        "width": f"{percentage}%",
                                        "height": "8px",
                                        "cornerRadius": "4px",
                                        "contents": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": c["border"]
                    },
                    {
                        "type": "text",
                        "text": f"ملاحظة: نفس النتيجة لو كتبت {name2} و {name1}",
                        "size": "xxs",
                        "color": c["text3"],
                        "align": "center",
                        "wrap": True,
                        "margin": "md"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "paddingAll": "12px",
                "backgroundColor": c["card"],
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "اعادة",
                            "text": "توافق"
                        },
                        "style": "secondary",
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "ايقاف",
                            "text": "ايقاف"
                        },
                        "style": "secondary",
                        "height": "sm",
                        "color": self.BUTTON_COLOR
                    }
                ]
            }
        }

        self.game_active = False
        return {
            "response": FlexMessage(
                alt_text="نتيجة التوافق",
                contents=FlexContainer.from_dict(bubble)
            ),
            "points": 0,
            "game_over": True
        }
