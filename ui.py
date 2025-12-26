"""Bot 65 - UI Module"""

from constants import GAME_LABELS
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction


class UI:
    THEMES = {
        "light": {
            "primary": "#1A1A1A",
            "text": "#2D2D2D",
            "text2": "#6B7280",
            "text3": "#9CA3AF",
            "bg": "#FFFFFF",
            "card": "#F9FAFB",
            "border": "#E5E7EB",
            "button": "#F5F5F5",
            "success": "#374151",
            "warning": "#6B7280",
            "error": "#4B5563"
        },
        "dark": {
            "primary": "#F9FAFB",
            "text": "#E5E7EB",
            "text2": "#9CA3AF",
            "text3": "#6B7280",
            "bg": "#111827",
            "card": "#1F2937",
            "border": "#374151",
            "button": "#F5F5F5",
            "success": "#D1D5DB",
            "warning": "#9CA3AF",
            "error": "#6B7280"
        }
    }

    @staticmethod
    def _c(theme):
        return UI.THEMES.get(theme, UI.THEMES["light"])

    @staticmethod
    def _button(label, text, c):
        return {
            "type": "button",
            "style": "secondary",
            "height": "sm",
            "action": {
                "type": "message",
                "label": label,
                "text": text
            },
            "color": c["button"]
        }

    @staticmethod
    def get_quick_reply():
        return QuickReply(
            items=[
                QuickReplyItem(action=MessageAction(label="بداية", text="بداية")),
                QuickReplyItem(action=MessageAction(label="العاب", text="العاب")),
                QuickReplyItem(action=MessageAction(label="سؤال", text="سؤال")),
                QuickReplyItem(action=MessageAction(label="تحدي", text="تحدي")),
                QuickReplyItem(action=MessageAction(label="اعتراف", text="اعتراف")),
                QuickReplyItem(action=MessageAction(label="منشن", text="منشن")),
                QuickReplyItem(action=MessageAction(label="اقتباس", text="اقتباس")),
                QuickReplyItem(action=MessageAction(label="موقف", text="موقف")),
                QuickReplyItem(action=MessageAction(label="شعر", text="شعر")),
                QuickReplyItem(action=MessageAction(label="خاص", text="خاص")),
                QuickReplyItem(action=MessageAction(label="مجهول", text="مجهول")),
                QuickReplyItem(action=MessageAction(label="نصيحة", text="نصيحة")),
                QuickReplyItem(action=MessageAction(label="مساعدة", text="مساعدة")),
            ]
        )

    @staticmethod
    def text_menu(theme="light"):
        c = UI._c(theme)

        texts = [
            ("سؤال", "سؤال"), ("تحدي", "تحدي"),
            ("اعتراف", "اعتراف"), ("منشن", "منشن"),
            ("اقتباس", "اقتباس"), ("موقف", "موقف"),
            ("شعر", "شعر"), ("خاص", "خاص"),
            ("مجهول", "مجهول"), ("نصيحة", "نصيحة")
        ]

        contents = [
            {
                "type": "text",
                "text": "قائمة النصوص",
                "size": "xl",
                "weight": "bold",
                "align": "center",
                "color": c["primary"]
            },
            {
                "type": "text",
                "text": "اختر نوع النص",
                "size": "xs",
                "align": "center",
                "color": c["text3"],
                "margin": "sm"
            },
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]

        for i in range(0, len(texts), 2):
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "xs",
                "margin": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": label,
                            "text": cmd
                        },
                        "color": c["button"],
                        "flex": 1
                    }
                    for label, cmd in texts[i:i + 2]
                ]
            })

        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": [UI._button("رجوع", "بداية", c)]
            }
        ])

        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": contents
            }
        }

    @staticmethod
    def games_menu(theme="light"):
        c = UI._c(theme)

        games = [
            ("خمن", "خمن"), ("اسرع", "اسرع"), ("اغنيه", "اغنيه"),
            ("ضد", "ضد"), ("تكوين", "تكوين"), ("فئه", "فئه"),
            ("ذكاء", "ذكاء"), ("ترتيب", "ترتيب"), ("لون", "لون"),
            ("روليت", "روليت"), ("سين", "سين"), ("سلسله", "سلسله"),
            ("لعبه", "لعبه"), ("حروف", "حروف"), ("توافق", "توافق"),
            ("مافيا", "مافيا")
        ]

        contents = [
            {
                "type": "text",
                "text": "قائمة الالعاب",
                "size": "xl",
                "weight": "bold",
                "align": "center",
                "color": c["primary"]
            },
            {
                "type": "text",
                "text": "اختر لعبتك المفضلة",
                "size": "xs",
                "align": "center",
                "color": c["text3"],
                "margin": "sm"
            },
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]

        for i in range(0, len(games), 3):
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "xs",
                "margin": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": GAME_LABELS.get(cmd, cmd),
                            "text": text
                        },
                        "color": c["button"],
                        "flex": 1
                    }
                    for cmd, text in games[i:i + 3]
                ]
            })

        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": [UI._button("رجوع", "بداية", c)]
            }
        ])

        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": contents
            }
        }
