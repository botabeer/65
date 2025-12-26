"""Bot 65 - UI Module"""

from constants import GAME_LABELS
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

class UI:
    THEMES = {
        "light": {
            "primary": "#1A1A1A", "text": "#2D2D2D", "text2": "#6B7280",
            "text3": "#9CA3AF", "bg": "#FFFFFF", "card": "#F9FAFB",
            "border": "#E5E7EB", "button": "#F5F5F5", "success": "#374151",
            "warning": "#6B7280", "error": "#4B5563"
        },
        "dark": {
            "primary": "#F9FAFB", "text": "#E5E7EB", "text2": "#9CA3AF",
            "text3": "#6B7280", "bg": "#111827", "card": "#1F2937",
            "border": "#374151", "button": "#F5F5F5", "success": "#D1D5DB",
            "warning": "#9CA3AF", "error": "#6B7280"
        }
    }

    @staticmethod
    def _c(theme):
        return UI.THEMES.get(theme, UI.THEMES["light"])
    
    @staticmethod
    def _button(label, text, c):
        return {
            "type": "button", "style": "secondary", "height": "sm",
            "action": {"type": "message", "label": label, "text": text},
            "color": c["button"]
        }

    @staticmethod
    def get_quick_reply():
        return QuickReply(items=[
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
            QuickReplyItem(action=MessageAction(label="مساعدة", text="مساعدة"))
        ])

    @staticmethod
    def welcome(name, registered, theme="light"):
        c = UI._c(theme)
        
        contents = [
            {"type": "text", "text": "Bot 65", "size": "xxl", 
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "text", "text": f"مرحبا {name}", "size": "lg", 
             "align": "center", "color": c["text"], "margin": "sm"},
            {
                "type": "box", "layout": "horizontal",
                "contents": [{
                    "type": "box", "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "الحالة", 
                         "size": "xxs", "color": c["text3"]},
                        {"type": "text", "text": "مسجل" if registered else "ضيف", 
                         "size": "sm", "weight": "bold", 
                         "color": c["success"] if registered else c["warning"]}
                    ], "flex": 1
                }],
                "backgroundColor": c["card"], "paddingAll": "12px",
                "cornerRadius": "8px", "margin": "md"
            },
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        contents.append({
            "type": "box", "layout": "horizontal", "spacing": "sm", "margin": "sm",
            "contents": [
                UI._button("تسجيل" if not registered else "تغيير", "تسجيل" if not registered else "تغيير", c),
                UI._button("انسحب", "انسحب", c)
            ]
        })
        
        contents.append({
            "type": "box", "layout": "horizontal", "spacing": "sm", "margin": "sm",
            "contents": [
                UI._button("نقاطي", "نقاطي", c),
                UI._button("الصدارة", "الصدارة", c)
            ]
        })
        
        contents.append({
            "type": "box", "layout": "vertical", "spacing": "xs", "margin": "sm",
            "contents": [
                {
                    "type": "box", "layout": "horizontal", "spacing": "xs",
                    "contents": [
                        UI._button("العاب", "العاب", c),
                        UI._button("سؤال", "سؤال", c),
                        UI._button("منشن", "منشن", c)
                    ]
                },
                {
                    "type": "box", "layout": "horizontal", "spacing": "xs", "margin": "xs",
                    "contents": [
                        UI._button("تحدي", "تحدي", c),
                        UI._button("اعتراف", "اعتراف", c),
                        UI._button("اقتباس", "اقتباس", c)
                    ]
                },
                {
                    "type": "box", "layout": "horizontal", "spacing": "xs", "margin": "xs",
                    "contents": [
                        UI._button("موقف", "موقف", c),
                        UI._button("شعر", "شعر", c),
                        UI._button("خاص", "خاص", c)
                    ]
                },
                {
                    "type": "box", "layout": "horizontal", "spacing": "xs", "margin": "xs",
                    "contents": [
                        UI._button("مجهول", "مجهول", c),
                        UI._button("نصيحة", "نصيحة", c)
                    ]
                }
            ]
        })
        
        contents.append({
            "type": "box", "layout": "horizontal", "spacing": "sm", "margin": "sm",
            "contents": [
                UI._button("ثيم", "ثيم", c),
                UI._button("مساعدة", "مساعدة", c)
            ]
        })
        
        contents.extend([
            {"type": "separator", "margin": "md", "color": c["border"]},
            {"type": "text", "text": "عبير الدوسري 2025", 
             "size": "xxs", "align": "center", "color": c["text3"], "margin": "md"}
        ])
        
        return {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "backgroundColor": c["bg"], "paddingAll": "20px",
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
            {"type": "text", "text": "قائمة الالعاب", "size": "xl", 
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "text", "text": "اختر لعبتك المفضلة", 
             "size": "xs", "align": "center", "color": c["text3"], "margin": "sm"},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        
        for i in range(0, len(games), 3):
            row_buttons = []
            for game_cmd, game_text in games[i:i+3]:
                row_buttons.append({
                    "type": "button", "style": "secondary", "height": "sm",
                    "action": {"type": "message", 
                              "label": GAME_LABELS.get(game_cmd, game_cmd), 
                              "text": game_text},
                    "color": c["button"], "flex": 1
                })
            
            contents.append({
                "type": "box", "layout": "horizontal",
                "spacing": "xs", "margin": "sm",
                "contents": row_buttons
            })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "text", "text": "اوامر اللعب: لمح - جاوب - ايقاف - انسحب", 
             "size": "xxs", "align": "center", "color": c["text3"], "margin": "sm"},
            {"type": "box", "layout": "horizontal", "margin": "md",
             "contents": [UI._button("رجوع", "بداية", c)]}
        ])
        
        return {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "backgroundColor": c["bg"], "paddingAll": "20px",
                "contents": contents
            }
        }

    @staticmethod
    def help_card(theme="light"):
        c = UI._c(theme)
        
        sections = [
            {
                "title": "الاوامر الاساسية",
                "items": ["بداية - الصفحة الرئيسية", "تسجيل - انشاء حساب",
                         "العاب - قائمة الالعاب", "نقاطي - احصائياتك",
                         "الصدارة - المتصدرين", "نص - الاوامر النصية"]
            },
            {
                "title": "اوامر اللعب",
                "items": ["لمح - الحصول على تلميح", "جاوب - اظهار الاجابة",
                         "ايقاف - انهاء اللعبة", "انسحب - الخروج من اللعبة"]
            },
            {
                "title": "الاوامر النصية",
                "items": [
                    "سؤال", "تحدي", "اعتراف", "منشن", "اقتباس",
                    "موقف", "شعر", "خاص", "مجهول", "نصيحة"
                ]
            }
        ]
        
        contents = [
            {"type": "text", "text": "المساعدة", "size": "xl", 
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        for section in sections:
            contents.append({
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": section['title'], 
                     "size": "sm", "weight": "bold", "color": c["text"], "margin": "md"}
                ] + [
                    {"type": "text", "text": f"• {item}", 
                     "size": "xs", "color": c["text2"], "margin": "xs", "wrap": True}
                    for item in section["items"]
                ],
                "backgroundColor": c["card"], "paddingAll": "12px",
                "cornerRadius": "8px", "margin": "md"
            })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "horizontal", "margin": "md",
             "contents": [UI._button("رجوع", "بداية", c)]}
        ])
        
        return {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "backgroundColor": c["bg"], "paddingAll": "20px",
                "contents": contents
            }
        }

    @staticmethod
    def stats(user, theme="light"):
        c = UI._c(theme)
        win_rate = int((user['wins'] / user['games'] * 100)) if user['games'] > 0 else 0
        
        stats = [
            {"label": "النقاط", "value": str(user['points']), "highlight": True},
            {"label": "الالعاب", "value": str(user['games'])},
            {"label": "الانتصارات", "value": str(user['wins'])},
            {"label": "نسبة الفوز", "value": f"{win_rate}%"}
        ]
        
        stats_contents = []
        for stat in stats:
            stats_contents.append({
                "type": "box", "layout": "horizontal", "margin": "sm",
                "contents": [
                    {"type": "text", "text": stat["label"], 
                     "size": "sm", "color": c["text2"], "flex": 1},
                    {"type": "text", "text": stat["value"], 
                     "size": "xl" if stat.get("highlight") else "md",
                     "weight": "bold",
                     "color": c["primary"] if stat.get("highlight") else c["text"],
                     "align": "end", "flex": 0}
                ]
            })
        
        contents = [
            {"type": "text", "text": "احصائياتك", "size": "xl", 
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "text", "text": user['name'], "size": "md", 
             "align": "center", "color": c["text2"], "margin": "sm"},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box", "layout": "vertical",
                "backgroundColor": c["card"], "cornerRadius": "8px",
                "paddingAll": "16px", "margin": "md",
                "contents": stats_contents
            },
            {
                "type": "box", "layout": "horizontal", "margin": "lg", "spacing": "sm",
                "contents": [
                    UI._button("رجوع", "بداية", c),
                    UI._button("الصدارة", "الصدارة", c)
                ]
            }
        ]
        
        return {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "backgroundColor": c["bg"], "paddingAll": "20px",
                "contents": contents
            }
        }

    @staticmethod
    def leaderboard(leaders, theme="light"):
        c = UI._c(theme)
        
        contents = [
            {"type": "text", "text": "المتصدرين", "size": "xl", 
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        for i, leader in enumerate(leaders[:10]):
            rank_display = f"{i + 1}."
            
            contents.append({
                "type": "box", "layout": "horizontal", "margin": "sm",
                "paddingAll": "8px" if i < 3 else "4px",
                "backgroundColor": c["card"] if i < 3 else "none",
                "cornerRadius": "8px" if i < 3 else "none",
                "contents": [
                    {"type": "text", "text": rank_display, 
                     "size": "md" if i < 3 else "sm",
                     "weight": "bold" if i < 3 else "regular",
                     "color": c["primary"] if i < 3 else c["text3"], "flex": 0},
                    {"type": "text", "text": leader['name'], 
                     "size": "sm", "color": c["text"], "flex": 3, "margin": "md"},
                    {"type": "text", "text": str(leader['points']), 
                     "size": "md" if i < 3 else "sm",
                     "weight": "bold" if i < 3 else "regular",
                     "color": c["primary"] if i < 3 else c["text2"],
                     "align": "end", "flex": 1}
                ]
            })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "horizontal", "margin": "md",
             "contents": [UI._button("رجوع", "بداية", c)]}
        ])
        
        return {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "backgroundColor": c["bg"], "paddingAll": "20px",
                "contents": contents
            }
        }
