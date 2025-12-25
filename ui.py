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

            "button": "#6B7280"  # رمادي موحد
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

            "button": "#6B7280"  # رمادي موحد
        }
    }

    @staticmethod
    def _c(theme):
        return UI.THEMES.get(theme, UI.THEMES["light"])

    # =========================
    # الصفحة الرئيسية
    # =========================
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

                    UI._row_buttons([
                        ("ثيم", "ثيم")
                    ], c),

                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {"type": "text", "text": "عبير الدوسري © 2025", "size": "xxs", "align": "center", "color": c["text3"]}
                ]
            }
        }

    # =========================
    # قائمة الألعاب
    # =========================
    @staticmethod
    def games_menu(theme="light"):
        c = UI._c(theme)

        contents = [
            {"type": "text", "text": "قائمة الألعاب", "size": "xl", "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]

        contents += UI._game_buttons([
            ["خمن", "اسرع"],
            ["اغنيه", "ضد"],
            ["تكوين", "فئه"],
            ["ذكاء", "ترتيب"],
            ["لون", "روليت"],
            ["سين"]
        ], c)

        contents.append({"type": "separator", "margin": "md", "color": c["border"]})

        contents += UI._game_buttons([
            ["سلسله", "لعبه"],
            ["حروف", "توافق"],
            ["مافيا"]
        ], c)

        contents.append({
            "type": "text",
            "text": "للخروج: انسحب أو ايقاف",
            "size": "xxs",
            "align": "center",
            "color": c["text3"],
            "margin": "md"
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

    # =========================
    # أدوات مساعدة
    # =========================
    @staticmethod
    def _row_buttons(buttons, c):
        return {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "margin": "md",
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
                "spacing": "sm",
                "margin": "md",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": c["button"],
                        "height": "sm",
                        "action": {"type": "message", "label": GAME_LABELS[g], "text": g}
                    } for g in row
                ]
            })
        return boxes
