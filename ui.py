"""Bot 65 - UI Module"""

from constants import GAME_LABELS


class UI:
    THEMES = {
        "light": {
            "primary": "#000000",
            "text": "#000000",
            "text2": "#4B5563",
            "text3": "#9CA3AF",
            "bg": "#FFFFFF",
            "card": "#F3F4F6",
            "border": "#D1D5DB",
            "success": "#6B7280",
            "info": "#6B7280",
            "warning": "#6B7280",
            "error": "#6B7280",
            "button": "#6B7280"
        },
        "dark": {
            "primary": "#FFFFFF",
            "text": "#FFFFFF",
            "text2": "#D1D5DB",
            "text3": "#9CA3AF",
            "bg": "#000000",
            "card": "#1F2937",
            "border": "#374151",
            "success": "#6B7280",
            "info": "#6B7280",
            "warning": "#6B7280",
            "error": "#6B7280",
            "button": "#6B7280"
        }
    }

    @staticmethod
    def _c(theme):
        return UI.THEMES.get(theme, UI.THEMES["light"])

    @staticmethod
    def welcome(name, registered, theme="light"):
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
                    {"type": "text", "text": "Bot 65", "size": "xxl", "weight": "bold", "align": "center", "color": c["primary"]},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": f"مرحبا {name}", "size": "lg", "align": "center", "weight": "bold", "color": c["text"], "margin": "md"},
                    {"type": "text", "text": "مسجل" if registered else "غير مسجل", "size": "xs", "align": "center", "color": c["text2"]},
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    UI._row_buttons([
                        ("تسجيل" if not registered else "تغيير", "تسجيل"),
                        ("انسحب", "انسحب")
                    ], c),
                    UI._row_buttons([
                        ("نقاطي", "نقاطي"),
                        ("الصدارة", "الصدارة")
                    ], c),
                    UI._row_buttons([
                        ("مساعدة", "مساعدة"),
                        ("العاب", "العاب")
                    ], c),
                    UI._row_buttons([("ثيم", "ثيم")], c),
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {"type": "text", "text": "عبير الدوسري 2025", "size": "xxs", "align": "center", "color": c["text3"]}
                ]
            }
        }

    @staticmethod
    def games_menu(theme="light"):
        c = UI._c(theme)
        contents = [
            {"type": "text", "text": "قائمة الالعاب", "size": "xxl", "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "text", "text": "اختر لعبتك المفضلة", "size": "sm", "align": "center", "color": c["text2"], "margin": "md"}
        ]
        
        game_rows = [
            ["خمن", "اسرع"],
            ["اغنيه", "ضد"],
            ["تكوين", "فئه"],
            ["ذكاء", "ترتيب"],
            ["لون", "روليت"],
            ["سين", "سلسله"],
            ["لعبه", "حروف"],
            ["توافق", "مافيا"]
        ]
        
        for row in game_rows:
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "md",
                "margin": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": c["button"],
                        "height": "md",
                        "action": {"type": "message", "label": GAME_LABELS[g], "text": g},
                        "flex": 1
                    } for g in row
                ]
            })
        
        contents.append({"type": "separator", "margin": "lg", "color": c["border"]})
        contents.append({
            "type": "text",
            "text": "للخروج: انسحب او ايقاف",
            "size": "xs",
            "align": "center",
            "color": c["text3"],
            "margin": "md"
        })
        
        contents.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "md",
            "margin": "lg",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": c["button"],
                    "height": "sm",
                    "action": {"type": "message", "label": "رجوع", "text": "بداية"}
                }
            ]
        })
        
        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "24px",
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
                    {"type": "text", "text": "المساعدة", "size": "xl", "weight": "bold", "align": "center", "color": c["primary"]},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": "الاوامر الاساسية", "size": "md", "weight": "bold", "color": c["text"], "margin": "lg"},
                    {"type": "text", "text": "بداية - الصفحة الرئيسية", "size": "sm", "color": c["text2"], "margin": "sm"},
                    {"type": "text", "text": "تسجيل - تسجيل او تغيير الاسم", "size": "sm", "color": c["text2"], "margin": "xs"},
                    {"type": "text", "text": "العاب - قائمة الالعاب", "size": "sm", "color": c["text2"], "margin": "xs"},
                    {"type": "text", "text": "نقاطي - احصائياتك", "size": "sm", "color": c["text2"], "margin": "xs"},
                    {"type": "text", "text": "الصدارة - المتصدرين", "size": "sm", "color": c["text2"], "margin": "xs"},
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {"type": "text", "text": "اوامر اللعب", "size": "md", "weight": "bold", "color": c["text"], "margin": "md"},
                    {"type": "text", "text": "لمح - الحصول على تلميح", "size": "sm", "color": c["text2"], "margin": "sm"},
                    {"type": "text", "text": "جاوب - اظهار الاجابة", "size": "sm", "color": c["text2"], "margin": "xs"},
                    {"type": "text", "text": "ايقاف - انهاء اللعبة", "size": "sm", "color": c["text2"], "margin": "xs"},
                    {"type": "text", "text": "انسحب - الانسحاب", "size": "sm", "color": c["text2"], "margin": "xs"},
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {"type": "text", "text": "اوامر نصية", "size": "md", "weight": "bold", "color": c["text"], "margin": "md"},
                    {"type": "text", "text": "سؤال - تحدي - اعتراف", "size": "sm", "color": c["text2"], "margin": "sm"},
                    {"type": "text", "text": "منشن - حكمة - موقف", "size": "sm", "color": c["text2"], "margin": "xs"},
                    UI._row_buttons([("رجوع", "بداية")], c)
                ]
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
                    {"type": "text", "text": "احصائياتك", "size": "xl", "weight": "bold", "align": "center", "color": c["primary"]},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": user['name'], "size": "lg", "weight": "bold", "align": "center", "color": c["text"], "margin": "lg"},
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
                                    {"type": "text", "text": "النقاط", "size": "sm", "color": c["text2"], "flex": 1},
                                    {"type": "text", "text": str(user['points']), "size": "lg", "weight": "bold", "color": c["primary"], "align": "end", "flex": 0}
                                ]
                            },
                            {"type": "separator", "margin": "md", "color": c["border"]},
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "md",
                                "contents": [
                                    {"type": "text", "text": "الالعاب", "size": "sm", "color": c["text2"], "flex": 1},
                                    {"type": "text", "text": str(user['games']), "size": "md", "weight": "bold", "color": c["text"], "align": "end", "flex": 0}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "sm",
                                "contents": [
                                    {"type": "text", "text": "الفوز", "size": "sm", "color": c["text2"], "flex": 1},
                                    {"type": "text", "text": str(user['wins']), "size": "md", "weight": "bold", "color": c["success"], "align": "end", "flex": 0}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "sm",
                                "contents": [
                                    {"type": "text", "text": "نسبة الفوز", "size": "sm", "color": c["text2"], "flex": 1},
                                    {"type": "text", "text": f"{win_rate}%", "size": "md", "weight": "bold", "color": c["info"], "align": "end", "flex": 0}
                                ]
                            }
                        ]
                    },
                    UI._row_buttons([("رجوع", "بداية")], c)
                ]
            }
        }

    @staticmethod
    def leaderboard(leaders, theme="light"):
        c = UI._c(theme)
        contents = [
            {"type": "text", "text": "المتصدرين", "size": "xl", "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        rank_colors = {0: "#FFD700", 1: "#C0C0C0", 2: "#CD7F32"}
        for i, leader in enumerate(leaders[:10]):
            rank_color = rank_colors.get(i, c["text2"])
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "margin": "md" if i == 0 else "sm",
                "contents": [
                    {"type": "text", "text": str(i + 1), "size": "sm", "color": rank_color, "flex": 0, "weight": "bold"},
                    {"type": "text", "text": leader['name'], "size": "sm", "color": c["text"], "flex": 3, "margin": "sm"},
                    {"type": "text", "text": str(leader['points']), "size": "sm", "color": c["primary"], "align": "end", "flex": 1, "weight": "bold"}
                ]
            })
        contents.append(UI._row_buttons([("رجوع", "بداية")], c))
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
    def _row_buttons(buttons, c):
        return {
            "type": "box",
            "layout": "horizontal",
            "spacing": "md",
            "margin": "lg",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": c["button"],
                    "height": "sm",
                    "action": {"type": "message", "label": label, "text": text}
                } for label, text in buttons
            ]
        }

    @staticmethod
    def _game_buttons(rows, c):
        boxes = []
        for row in rows:
            boxes.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "md",
                "margin": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": c["button"],
                        "height": "md",
                        "action": {"type": "message", "label": GAME_LABELS[g], "text": g},
                        "flex": 1
                    } for g in row
                ]
            })
        return boxes
