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
            "button": "#374151",
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
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "يجب التسجيل للعب",
                        "size": "sm",
                        "align": "center",
                        "color": c["error"],
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "اكتب اسمك في الشات",
                        "size": "xs",
                        "align": "center",
                        "color": c["text3"],
                        "margin": "xs"
                    }
                ],
                "backgroundColor": c["card"],
                "paddingAll": "12px",
                "cornerRadius": "8px",
                "margin": "md"
            })

        contents.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "xs",
            "margin": "md",
            "contents": [
                UI._button("تغيير الاسم" if registered else "تسجيل", "تسجيل", c),
                UI._button("انسحب", "انسحب", c)
            ]
        })

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
                        "text": "دليل الاستخدام",
                        "size": "xl",
                        "weight": "bold",
                        "align": "center",
                        "color": c["primary"]
                    },
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الأوامر الأساسية",
                                "size": "sm",
                                "weight": "bold",
                                "color": c["text"],
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "• بداية - العودة للقائمة الرئيسية\n• تسجيل - تسجيل اسمك في البوت\n• نقاطي - عرض نقاطك وإحصائياتك\n• الصدارة - عرض قائمة المتصدرين",
                                "size": "xs",
                                "color": c["text2"],
                                "wrap": True,
                                "margin": "xs"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الألعاب",
                                "size": "sm",
                                "weight": "bold",
                                "color": c["text"],
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "• العاب - قائمة جميع الألعاب\n• اكتب اسم اللعبة لبدء اللعب\n• لمح - للحصول على مساعدة\n• جاوب - لعرض الإجابة\n• ايقاف - لإيقاف اللعبة",
                                "size": "xs",
                                "color": c["text2"],
                                "wrap": True,
                                "margin": "xs"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "النصوص",
                                "size": "sm",
                                "weight": "bold",
                                "color": c["text"],
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "• سؤال - أسئلة عميقة\n• منشن - منشن عشوائي\n• تحدي - تحديات ممتعة\n• اعتراف - اعترافات\n• مجهول - رسائل مجهولة\n• خاص - أسئلة خاصة\n• اقتباس - اقتباسات ملهمة\n• موقف - مواقف افتراضية\n• نصيحة - نصائح حياتية\n• شعر - أبيات شعرية",
                                "size": "xs",
                                "color": c["text2"],
                                "wrap": True,
                                "margin": "xs"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "ملاحظات",
                                "size": "sm",
                                "weight": "bold",
                                "color": c["text"],
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "• يجب التسجيل أولاً للعب الألعاب\n• استخدم انسحب للخروج من أي لعبة\n• يمكنك تغيير الثيم بين الفاتح والداكن\n• النقاط تُحفظ تلقائياً بعد كل لعبة",
                                "size": "xs",
                                "color": c["text2"],
                                "wrap": True,
                                "margin": "xs"
                            }
                        ]
                    },
                    {"type": "separator", "margin": "lg", "color": c["border"]},
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

    @staticmethod
    def games_menu(theme="light"):
        c = UI._c(theme)

        games = [
            ("خمن", "خمن"), ("اسرع", "اسرع"), ("توافق", "توافق"),
            ("اغنيه", "اغنيه"), ("ضد", "ضد"), ("سلسله", "سلسله"),
            ("تكوين", "تكوين"), ("فئه", "فئه"), ("لعبه", "لعبه"),
            ("ذكاء", "ذكاء"), ("ترتيب", "ترتيب"), ("حروف", "حروف"),
            ("مافيا", "مافيا"), ("لون", "لون"), ("روليت", "روليت"),
            ("سين", "سين")
        ]

        contents = [
            {
                "type": "text",
                "text": "قائمة الألعاب",
                "size": "xl",
                "weight": "bold",
                "align": "center",
                "color": c["primary"]
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
                    UI._button(label, cmd, c) for label, cmd in games[i:i + 3]
                ]
            })

        contents.extend([
            {"type": "separator", "margin": "md", "color": c["border"]},
            {
                "type": "text",
                "text": "اكتب صعوبة ١ إلى ٥ لتغيير مستوى الصعوبة",
                "size": "xxs",
                "color": c["text3"],
                "align": "center",
                "margin": "xs"
            },
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

        win_rate = int((user['wins'] / user['games'] * 100)) if user['games'] > 0 else 0

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
                        "text": "إحصائياتك",
                        "size": "xl",
                        "weight": "bold",
                        "align": "center",
                        "color": c["primary"]
                    },
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": user['name'],
                                "size": "lg",
                                "weight": "bold",
                                "color": c["text"],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": f"{user['points']} نقطة",
                                "size": "xxl",
                                "weight": "bold",
                                "color": c["primary"],
                                "align": "center",
                                "margin": "sm"
                            }
                        ],
                        "backgroundColor": c["card"],
                        "cornerRadius": "12px",
                        "paddingAll": "16px",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "عدد الألعاب",
                                        "size": "xs",
                                        "color": c["text2"],
                                        "align": "center"
                                    },
                                    {
                                        "type": "text",
                                        "text": str(user['games']),
                                        "size": "xl",
                                        "weight": "bold",
                                        "color": c["text"],
                                        "align": "center",
                                        "margin": "xs"
                                    }
                                ],
                                "flex": 1
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "الانتصارات",
                                        "size": "xs",
                                        "color": c["text2"],
                                        "align": "center"
                                    },
                                    {
                                        "type": "text",
                                        "text": str(user['wins']),
                                        "size": "xl",
                                        "weight": "bold",
                                        "color": c["success"],
                                        "align": "center",
                                        "margin": "xs"
                                    }
                                ],
                                "flex": 1
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "نسبة الفوز",
                                        "size": "xs",
                                        "color": c["text2"],
                                        "align": "center"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{win_rate}%",
                                        "size": "xl",
                                        "weight": "bold",
                                        "color": c["primary"],
                                        "align": "center",
                                        "margin": "xs"
                                    }
                                ],
                                "flex": 1
                            }
                        ],
                        "margin": "md"
                    },
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "spacing": "xs",
                        "contents": [
                            UI._button("الصدارة", "الصدارة", c),
                            UI._button("رجوع", "بداية", c)
                        ]
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
                "text": "قائمة المتصدرين",
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
                "text": "لا يوجد لاعبون بعد",
                "size": "sm",
                "color": c["text2"],
                "align": "center",
                "margin": "md"
            })
        else:
            for i, leader in enumerate(leaders[:10]):
                rank_color = c["primary"] if i < 3 else c["text2"]
                contents.append({
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{i + 1}",
                            "size": "sm",
                            "weight": "bold",
                            "color": rank_color,
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": leader['name'],
                            "size": "sm",
                            "color": c["text"],
                            "flex": 3,
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": str(leader['points']),
                            "size": "sm",
                            "weight": "bold",
                            "color": c["primary"],
                            "align": "end",
                            "flex": 1
                        }
                    ],
                    "paddingAll": "8px",
                    "margin": "sm"
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
