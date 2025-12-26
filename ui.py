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
            "button": "#94A3B8",
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
            "button": "#64748B",
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
            "color": c["button"],
            "flex": 1
        }

    @staticmethod
    def get_quick_reply():
        return QuickReply(items=[
            QuickReplyItem(action=MessageAction(label="بداية", text="بداية")),
            QuickReplyItem(action=MessageAction(label="العاب", text="العاب")),
            QuickReplyItem(action=MessageAction(label="سؤال", text="سؤال")),
            QuickReplyItem(action=MessageAction(label="منشن", text="منشن")),
            QuickReplyItem(action=MessageAction(label="تحدي", text="تحدي")),
            QuickReplyItem(action=MessageAction(label="اعتراف", text="اعتراف")),
            QuickReplyItem(action=MessageAction(label="مجهول", text="مجهول")),
            QuickReplyItem(action=MessageAction(label="خاص", text="خاص")),
            QuickReplyItem(action=MessageAction(label="اقتباس", text="اقتباس")),
            QuickReplyItem(action=MessageAction(label="موقف", text="موقف")),
            QuickReplyItem(action=MessageAction(label="نصيحة", text="نصيحة")),
            QuickReplyItem(action=MessageAction(label="شعر", text="شعر")),
            QuickReplyItem(action=MessageAction(label="مساعدة", text="مساعدة"))
        ])

    @staticmethod
    def welcome(name, registered, theme="light"):
        c = UI._c(theme)

        contents = [
            {
                "type": "text",
                "text": "Bot 65",
                "size": "xxl",
                "weight": "bold",
                "align": "center",
                "color": c["primary"]
            },
            {
                "type": "text",
                "text": f"مرحبا {name}",
                "size": "md",
                "align": "center",
                "color": c["text2"],
                "margin": "xs"
            },
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]

        if not registered:
            contents.append({
                "type": "text",
                "text": "يجب التسجيل أولاً",
                "size": "sm",
                "align": "center",
                "color": c["error"],
                "margin": "md"
            })

        contents.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "xs",
            "margin": "md",
            "contents": [
                UI._button("تسجيل" if not registered else "تغيير", "تسجيل" if not registered else "تغيير", c),
                UI._button("انسحب", "انسحب", c)
            ]
        })

        contents.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "xs",
            "margin": "xs",
            "contents": [
                UI._button("العاب", "العاب", c),
                UI._button("نص", "نص", c)
            ]
        })

        contents.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "xs",
            "margin": "xs",
            "contents": [
                UI._button("ثيم", "ثيم", c),
                UI._button("مساعدة", "مساعدة", c)
            ]
        })

        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "text",
                "text": "تم إنشاء هذا البوت بواسطة عبير الدوسري © 2025",
                "size": "xxs",
                "color": c["text3"],
                "align": "center"
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
    def help_card(theme="light"):
        c = UI._c(theme)

        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "المساعدة",
                        "size": "xl",
                        "weight": "bold",
                        "align": "center",
                        "color": c["primary"]
                    },
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "text",
                        "text": "الأوامر:\nبداية - العاب - نص\nسؤال - منشن - تحدي - اعتراف\nاقتباس - موقف - شعر - خاص\nمجهول - نصيحة",
                        "size": "xs",
                        "wrap": True,
                        "color": c["text2"]
                    },
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [UI._button("رجوع", "بداية", c)]
                    }
                ]
            }
        }

    @staticmethod
    def text_menu(theme="light"):
        c = UI._c(theme)

        texts = [
            "سؤال", "منشن", "تحدي",
            "اعتراف", "مجهول", "خاص",
            "اقتباس", "موقف", "نصيحة",
            "شعر"
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
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]

        for i in range(0, len(texts), 3):
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "xs",
                "margin": "sm",
                "contents": [
                    UI._button(t, t, c) for t in texts[i:i + 3]
                ]
            })

        contents.append({
            "type": "box",
            "layout": "horizontal",
            "margin": "md",
            "contents": [UI._button("رجوع", "بداية", c)]
        })

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
