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
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["card"],
                "cornerRadius": "8px",
                "paddingAll": "12px",
                "margin": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "يجب التسجيل اولا",
                        "size": "sm",
                        "color": c["text"],
                        "align": "center"
                    }
                ]
            })

        # السطر الأول
        row1 = []
        if not registered:
            row1.append(UI._button("تسجيل", "تسجيل", c))
        else:
            row1.append(UI._button("تغيير", "تغيير", c))
        row1.append(UI._button("انسحب", "انسحب", c))
        
        contents.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "xs",
            "margin": "md",
            "contents": row1
        })

        # السطر الثاني
        contents.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "xs",
            "margin": "xs",
            "contents": [
                UI._button("نقاطي", "نقاطي", c),
                UI._button("الصدارة", "الصدارة", c)
            ]
        })

        # السطر الثالث
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

        # السطر الرابع
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

        # الحقوق
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "text",
                "text": "تم إنشاء هذا البوت بواسطة عبير الدوسري @ 2025",
                "size": "xxs",
                "color": c["text3"],
                "align": "center",
                "margin": "md"
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
                        "text": "الأوامر المتاحة:",
                        "size": "sm",
                        "weight": "bold",
                        "color": c["text"],
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "بداية - القائمة الرئيسية\nالعاب - قائمة الألعاب\nنص - قائمة النصوص\nنقاطي - عرض نقاطك\nالصدارة - عرض المتصدرين\nتسجيل - تسجيل حساب جديد\nثيم - تغيير المظهر",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "sm"
                    },
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [UI._button("رجوع", "بداية", c)]
                    }
                ]
            }
        }

    @staticmethod
    def text_menu(theme="light"):
        c = UI._c(theme)

        texts = [
            ("سؤال", "سؤال"), ("تحدي", "تحدي"),
            ("اعتراف", "اعتراف"), ("منشن", "منشن"),
            ("اقتباس", "اقتباس"), ("موقف", "موقف")
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

    @staticmethod
    def stats(user, theme="light"):
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
                        "text": "احصائياتك",
                        "size": "xl",
                        "weight": "bold",
                        "align": "center",
                        "color": c["primary"]
                    },
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": c["card"],
                        "cornerRadius": "12px",
                        "paddingAll": "16px",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {"type": "text", "text": "الاسم:", "size": "sm", "color": c["text2"], "flex": 1},
                                    {"type": "text", "text": user['name'], "size": "sm", "weight": "bold", "color": c["text"], "align": "end", "flex": 2}
                                ],
                                "margin": "sm"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {"type": "text", "text": "النقاط:", "size": "sm", "color": c["text2"], "flex": 1},
                                    {"type": "text", "text": str(user['points']), "size": "sm", "weight": "bold", "color": c["primary"], "align": "end", "flex": 2}
                                ],
                                "margin": "sm"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {"type": "text", "text": "الألعاب:", "size": "sm", "color": c["text2"], "flex": 1},
                                    {"type": "text", "text": str(user['games']), "size": "sm", "weight": "bold", "color": c["text"], "align": "end", "flex": 2}
                                ],
                                "margin": "sm"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {"type": "text", "text": "الانتصارات:", "size": "sm", "color": c["text2"], "flex": 1},
                                    {"type": "text", "text": str(user['wins']), "size": "sm", "weight": "bold", "color": c["success"], "align": "end", "flex": 2}
                                ],
                                "margin": "sm"
                            }
                        ]
                    },
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [UI._button("رجوع", "بداية", c)]
                    }
                ]
            }
        }

    @staticmethod
    def leaderboard(leaders, theme="light"):
        c = UI._c(theme)
        
        contents = [
            {
                "type": "text",
                "text": "لوحة الصدارة",
                "size": "xl",
                "weight": "bold",
                "align": "center",
                "color": c["primary"]
            },
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]

        if not leaders:
            contents.append({
                "type": "text",
                "text": "لا يوجد متصدرين بعد",
                "size": "sm",
                "color": c["text2"],
                "align": "center",
                "margin": "md"
            })
        else:
            for i, leader in enumerate(leaders[:10], 1):
                medal = ""
                if i == 1:
                    medal = "المركز الأول"
                elif i == 2:
                    medal = "المركز الثاني"
                elif i == 3:
                    medal = "المركز الثالث"
                else:
                    medal = f"المركز {i}"

                contents.append({
                    "type": "box",
                    "layout": "horizontal",
                    "backgroundColor": c["card"],
                    "cornerRadius": "8px",
                    "paddingAll": "12px",
                    "margin": "sm",
                    "contents": [
                        {"type": "text", "text": medal, "size": "xs", "color": c["text3"], "flex": 0},
                        {"type": "text", "text": leader['name'], "size": "sm", "color": c["text"], "flex": 2, "margin": "md"},
                        {"type": "text", "text": str(leader['points']), "size": "sm", "weight": "bold", "color": c["primary"], "align": "end", "flex": 1}
                    ]
                })

        contents.extend([
            {"type": "separator", "margin": "md", "color": c["border"]},
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
