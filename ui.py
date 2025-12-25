"""Bot 65 - UI Module"""

from constants import GAME_LABELS

class UI:
    THEMES = {
        "light": {
            "primary": "#000000",      # أسود للنصوص الأساسية
            "text": "#000000",         # أسود للنصوص العادية
            "text2": "#4B5563",        # رمادي متوسط
            "text3": "#9CA3AF",        # رمادي فاتح
            "bg": "#FFFFFF",           # أبيض للخلفية
            "card": "#F3F4F6",         # رمادي فاتح للبطاقات
            "border": "#D1D5DB",       # رمادي متوسط للفواصل
            "progress_bg": "#E5E7EB",  # رمادي فاتح لشريط التقدم الخلفي
            "progress_fill": "#000000", # أسود لشريط التقدم المملوء
            # ألوان الحالة
            "success": "#000000",
            "warning": "#4B5563",
            "error": "#9CA3AF",
            "info": "#000000"
        },
        "dark": {
            "primary": "#FFFFFF",      # أبيض للنصوص الأساسية
            "text": "#FFFFFF",         # أبيض للنصوص العادية
            "text2": "#D1D5DB",        # رمادي فاتح للنصوص الثانوية
            "text3": "#9CA3AF",        # رمادي متوسط للنصوص الثالثة
            "bg": "#000000",           # أسود للخلفية
            "card": "#1F2937",         # رمادي داكن للبطاقات
            "border": "#374151",       # رمادي غامق للفواصل
            "progress_bg": "#374151",  # رمادي غامق لشريط التقدم الخلفي
            "progress_fill": "#FFFFFF", # أبيض لشريط التقدم المملوء
            # ألوان الحالة
            "success": "#FFFFFF",
            "warning": "#D1D5DB",
            "error": "#9CA3AF",
            "info": "#FFFFFF"
        }
    }

    @staticmethod
    def _c(theme):
        return UI.THEMES.get(theme, UI.THEMES['light'])

    @staticmethod
    def welcome(name, registered, theme='light'):
        c = UI._c(theme)
        status = "مسجل" if registered else "غير مسجل"
        status_color = c['success'] if registered else c['warning']

        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "Bot 65",
                        "weight": "bold",
                        "size": "xxl",
                        "color": c['primary'],
                        "align": "center"
                    },
                    {"type": "separator", "margin": "md", "color": c['border']},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": f"مرحبا {name}", "size": "lg", "color": c['text'], "align": "center", "weight": "bold"},
                            {"type": "text", "text": status, "size": "xs", "color": status_color, "align": "center", "margin": "xs"}
                        ],
                        "margin": "md"
                    },
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._main_buttons(c, registered),
                    {"type": "separator", "margin": "lg", "color": c['border']},
                    {"type": "text", "text": "تم إنشاء هذا البوت بواسطة", "size": "xxs", "color": c['text3'], "align": "center", "margin": "md"},
                    {"type": "text", "text": "عبير الدوسري @ 2025", "size": "xs", "color": c['text2'], "align": "center", "weight": "bold", "margin": "xs"}
                ],
                "paddingAll": "20px",
                "backgroundColor": c['bg']
            }
        }

    @staticmethod
    def _main_buttons(c, registered):
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "button", "action": {"type": "message", "label": "تسجيل" if not registered else "تغيير", "text": "تسجيل" if not registered else "تغيير"}, "style": "primary", "color": c['primary'], "height": "sm", "flex": 1},
                        {"type": "button", "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"}, "style": "primary", "color": c['success'], "height": "sm", "flex": 1}
                    ],
                    "spacing": "sm"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "button", "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"}, "style": "primary", "color": c['warning'], "height": "sm", "flex": 1},
                        {"type": "button", "action": {"type": "message", "label": "العاب", "text": "العاب"}, "style": "primary", "color": c['info'], "height": "sm", "flex": 1}
                    ],
                    "spacing": "sm",
                    "margin": "sm"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "button", "action": {"type": "message", "label": "مساعدة", "text": "مساعدة"}, "style": "secondary", "height": "sm", "flex": 1},
                        {"type": "button", "action": {"type": "message", "label": "ثيم", "text": "ثيم"}, "style": "secondary", "height": "sm", "flex": 1}
                    ],
                    "spacing": "sm",
                    "margin": "sm"
                },
                {"type": "button", "action": {"type": "message", "label": "انسحب", "text": "انسحب"}, "style": "secondary", "color": c['error'], "height": "sm", "margin": "sm"}
            ]
        }

    @staticmethod
    def games_menu(theme='light'):
        c = UI._c(theme)
        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "قائمة الالعاب", "weight": "bold", "size": "xl", "color": c['primary'], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._game_buttons_individual(c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._game_buttons_group(c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    {"type": "text", "text": "للخروج اضغط: ايقاف او انسحب", "size": "xxs", "color": c['text3'], "align": "center", "margin": "md"}
                ],
                "paddingAll": "20px",
                "backgroundColor": c['bg']
            }
        }

    @staticmethod
    def _game_buttons_individual(c):
        rows = [
            ['خمن', 'اسرع'],
            ['اغنيه', 'ضد'],
            ['تكوين', 'فئه'],
            ['ذكاء', 'ترتيب'],
            ['لون', 'روليت'],
            ['سين']
        ]
        contents = []
        for row in rows:
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {"type": "button", "action": {"type": "message", "label": GAME_LABELS[g], "text": g}, "style": "primary", "color": c['primary'], "height": "sm"} for g in row
                ],
                "spacing": "sm",
                "margin": "md"
            })
        return contents

    @staticmethod
    def _game_buttons_group(c):
        rows = [
            ['سلسله', 'لعبه'],
            ['حروف', 'توافق'],
            ['مافيا']
        ]
        contents = []
        for row in rows:
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {"type": "button", "action": {"type": "message", "label": GAME_LABELS[g], "text": g}, "style": "secondary", "height": "sm", "color": c['error'] if g == 'مافيا' else c['primary']} for g in row
                ],
                "spacing": "sm",
                "margin": "md"
            })
        return contents

    @staticmethod
    def help_card(theme='light'):
        c = UI._c(theme)
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "دليل الاستخدام", "weight": "bold", "size": "xl", "color": c['primary'], "align": "center"},
                    {"type": "separator", "margin": "lg", "color": c['border']},
                    UI._section("الاوامر الاساسية", "بداية - العاب - نقاطي - الصدارة - تسجيل - ثيم", c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._section("اوامر نصية", "سؤال - تحدي - اعتراف - منشن - حكمة - موقف", c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._section("الالعاب الفردية", "خمن - اسرع - اغنيه - ضد - تكوين - فئه - ذكاء - ترتيب - لون - روليت - سين", c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._section("الالعاب الجماعية", "سلسله - لعبه - حروف - توافق - مافيا", c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._section("اثناء اللعب", "لمح: تلميح | جاوب: عرض الاجابة | انسحب: الخروج", c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._section("التحكم بالصعوبة", "صعوبة 1 الى صعوبة 5 (قبل بدء اللعبة)", c)
                ],
                "paddingAll": "20px",
                "backgroundColor": c['bg']
            }
        }

    @staticmethod
    def stats(user, theme='light'):
        c = UI._c(theme)
        rate = round((user['wins'] / user['games'] * 100) if user['games'] > 0 else 0)
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "احصائياتك", "weight": "bold", "size": "xl", "color": c['primary'], "align": "center"},
                    {"type": "separator", "margin": "lg", "color": c['border']},
                    {"type": "text", "text": user['name'], "size": "xl", "color": c['text'], "align": "center", "weight": "bold", "margin": "lg"},
                    {"type": "separator", "margin": "lg", "color": c['border']},
                    UI._stat("النقاط", str(user['points']), c['success'], c),
                    UI._stat("الالعاب", str(user['games']), c['info'], c),
                    UI._stat("الفوز", str(user['wins']), c['primary'], c),
                    UI._stat("نسبة الفوز", f"{rate}%", c['warning'], c)
                ],
                "paddingAll": "20px",
                "backgroundColor": c['bg']
            }
        }

    @staticmethod
    def leaderboard(leaders, theme='light'):
        c = UI._c(theme)
        contents = [{"type": "text", "text": "لوحة الصدارة", "weight": "bold", "size": "xl", "color": c['primary'], "align": "center"},
                    {"type": "separator", "margin": "lg", "color": c['border']}]

        if not leaders:
            contents.append({"type": "text", "text": "لا توجد بيانات", "size": "sm", "color": c['text2'], "align": "center", "margin": "lg"})
        else:
            for i, leader in enumerate(leaders[:20], 1):
                contents.append(UI._leader(str(i), leader['name'], str(leader['points']), c))

        return {"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": contents, "paddingAll": "20px", "backgroundColor": c['bg']}}

    @staticmethod
    def _section(title, content, c):
        return {"type": "box", "layout": "vertical",
                "contents": [{"type": "text", "text": title, "weight": "bold", "size": "sm", "color": c['primary']},
                             {"type": "text", "text": content, "size": "xs", "color": c['text2'], "wrap": True, "margin": "xs"}],
                "margin": "md"}

    @staticmethod
    def _stat(label, value, value_color, c):
        return {"type": "box", "layout": "baseline",
                "contents": [{"type": "text", "text": label, "size": "sm", "color": c['text2'], "flex": 3},
                             {"type": "text", "text": value, "size": "lg", "weight": "bold", "color": value_color, "align": "end", "flex": 2}],
                "margin": "md"}

    @staticmethod
    def _leader(rank, name, points, c):
        rank_colors = {"1": "#FFD700", "2": "#C0C0C0", "3": "#CD7F32"}
        rank_color = rank_colors.get(rank, c['text2'])
        return {"type": "box", "layout": "baseline",
                "contents": [{"type": "text", "text": rank, "size": "sm", "color": rank_color, "flex": 0, "weight": "bold"},
                             {"type": "text", "text": name, "size": "sm", "color": c['text'], "flex": 4, "margin": "sm"},
                             {"type": "text", "text": points, "size": "sm", "weight": "bold", "color": c['success'], "align": "end", "flex": 1}],
                "margin": "sm", "paddingAll": "8px"}
