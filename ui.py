from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

class UI:
    """واجهة مستخدم احترافية ومحسّنة"""

    THEMES = {
        "light": {
            "primary": "#1E293B",
            "secondary": "#475569",
            "text": "#334155",
            "text2": "#64748B",
            "text3": "#94A3B8",
            "bg": "#F8FAFC",
            "card": "#F8FAFC",
            "border": "#E2E8F0",
            "button": "#3B82F6",
            "button_text": "#FFFFFF",
            "success": "#10B981",
            "warning": "#F59E0B",
            "error": "#EF4444",
            "accent": "#3B82F6"
        },
        "dark": {
            "primary": "#F1F5F9",
            "secondary": "#CBD5E1",
            "text": "#E2E8F0",
            "text2": "#94A3B8",
            "text3": "#64748B",
            "bg": "#0F172A",
            "card": "#0F172A",
            "border": "#334155",
            "button": "#3B82F6",
            "button_text": "#FFFFFF",
            "success": "#10B981",
            "warning": "#F59E0B",
            "error": "#EF4444",
            "accent": "#60A5FA"
        }
    }

    @staticmethod
    def _c(theme):
        """الحصول على ألوان الثيم"""
        return UI.THEMES.get(theme, UI.THEMES["dark"])

    @staticmethod
    def _btn(label, text, theme="dark", style="primary"):
        """إنشاء زر موحد اللون"""
        bg_color = "#F5F5F5"
        text_color = "#000000"
        return {
            "type": "button",
            "style": "primary" if style == "primary" else "secondary",
            "height": "sm",
            "action": {"type": "message", "label": label, "text": text},
            "color": bg_color,
            "flex": 1
        }

    @staticmethod
    def get_quick_reply():
        items = [
            ("بداية", "بداية"), ("العاب", "العاب"), ("نص", "نص"), ("سؤال", "سؤال"),
            ("منشن", "منشن"), ("تحدي", "تحدي"), ("اعتراف", "اعتراف"), ("مجهول", "مجهول"),
            ("خاص", "خاص"), ("موقف", "موقف"), ("نصيحة", "نصيحة"), ("مساعدة", "مساعدة")
        ]
        return QuickReply(
            items=[QuickReplyItem(action=MessageAction(label=l, text=t)) for l, t in items]
        )

    @staticmethod
    def welcome(name, registered, theme="dark"):
        c = UI._c(theme)
        contents = [
            {"type": "text", "text": "Bot 65", "size": "xxl", "weight": "bold",
             "align": "center", "color": c["primary"]},
            {"type": "text", "text": f"مرحبا {name}", "size": "md",
             "align": "center", "color": c["text2"], "margin": "xs"},
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        if not registered:
            contents.append({
                "type": "box", "layout": "vertical", "margin": "lg",
                "contents": [
                    {"type": "text", "text": "يجب التسجيل للعب", "size": "sm",
                     "align": "center", "color": c["error"], "weight": "bold"},
                    {"type": "text", "text": "اكتب: تسجيل", "size": "xs",
                     "align": "center", "color": c["text3"], "margin": "xs"}
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "12px", "cornerRadius": "8px"
            })
        contents.extend([
            {"type": "box", "layout": "horizontal", "spacing": "xs", "margin": "lg",
             "contents": [UI._btn("تسجيل", "تسجيل", theme),
                          UI._btn("انسحب", "انسحب", theme, "secondary")]},
            {"type": "box", "layout": "horizontal", "spacing": "xs", "margin": "sm",
             "contents": [UI._btn("نقاطي", "نقاطي", theme),
                          UI._btn("الصدارة", "الصدارة", theme)]},
            {"type": "box", "layout": "horizontal", "spacing": "xs", "margin": "sm",
             "contents": [UI._btn("نص", "نص", theme), UI._btn("العاب", "العاب", theme)]},
            {"type": "box", "layout": "horizontal", "spacing": "xs", "margin": "sm",
             "contents": [UI._btn("ثيم", "ثيم", theme, "secondary"),
                          UI._btn("مساعدة", "مساعدة", theme, "secondary")]},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "text", "text": "تم إنشاء هذا البوت بواسطة عبير الدوسري @ 2025",
             "size": "xxs", "color": c["text3"], "align": "center", "margin": "md"}
        ])
        return {"type": "bubble", "size": "mega",
                "body": {"type": "box", "layout": "vertical",
                         "backgroundColor": c["bg"], "paddingAll": "20px",
                         "contents": contents}}

    @staticmethod
    def text_commands_menu(theme="dark"):
        c = UI._c(theme)
        commands = [("سؤال", "سؤال"), ("منشن", "منشن"), ("تحدي", "تحدي"),
                    ("اعتراف", "اعتراف"), ("مجهول", "مجهول"), ("خاص", "خاص"),
                    ("نصيحة", "نصيحة"), ("موقف", "موقف"), ("اقتباس", "اقتباس")]
        contents = [
            {"type": "text", "text": "قائمة النصوص", "size": "xl", "weight": "bold",
             "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        for i in range(0, len(commands), 3):
            row_buttons = [UI._btn(l, t, theme) for l, t in commands[i:i+3]]
            contents.append({"type": "box", "layout": "horizontal", "spacing": "xs",
                             "margin": "sm" if i > 0 else "lg", "contents": row_buttons})
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "horizontal", "margin": "md",
             "contents": [UI._btn("رجوع", "بداية", theme, "secondary")]}
        ])
        return {"type": "bubble", "size": "mega",
                "body": {"type": "box", "layout": "vertical",
                         "backgroundColor": c["bg"], "paddingAll": "20px",
                         "contents": contents}}

    @staticmethod
    def games_menu(theme="dark"):
        c = UI._c(theme)
        games = [("فئه", "فئه"), ("اسرع", "اسرع"), ("توافق", "توافق"),
                 ("اغنيه", "اغنيه"), ("ضد", "ضد"), ("سلسله", "سلسله"),
                 ("تكوين", "تكوين"), ("لغز", "لغز"), ("ترتيب", "ترتيب"),
                 ("حرف", "حرف"), ("لون", "لون"), ("مافيا", "مافيا")]
        contents = [
            {"type": "text", "text": "قائمة الالعاب", "size": "xl", "weight": "bold",
             "align": "center", "color": c["primary"]},
            {"type": "text", "text": "اختر لعبة للبدء", "size": "xs",
             "color": c["text2"], "align": "center", "margin": "xs"},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        for i in range(0, len(games), 3):
            contents.append({"type": "box", "layout": "horizontal", "spacing": "xs",
                             "margin": "sm" if i > 0 else "lg",
                             "contents": [UI._btn(l, t, theme) for l, t in games[i:i+3]]})
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "horizontal", "margin": "md",
             "contents": [UI._btn("رجوع", "بداية", theme, "secondary")]}
        ])
        return {"type": "bubble", "size": "mega",
                "body": {"type": "box", "layout": "vertical",
                         "backgroundColor": c["bg"], "paddingAll": "20px",
                         "contents": contents}}

    @staticmethod
    def help_card(theme="dark"):
        c = UI._c(theme)
        sections = [
            {"title": "الاوامر الاساسية", "items": ["بداية - القائمة الرئيسية",
                                                    "تسجيل - تسجيل اسمك",
                                                    "نقاطي - احصائياتك",
                                                    "الصدارة - قائمة المتصدرين",
                                                    "ثيم - تغيير المظهر",
                                                    "انسحب - الخروج من اللعبة"]},
            {"title": "اوامر النصوص", "items": ["نص - قائمة النصوص", "سؤال - اسئلة متنوعة",
                                                "تحدي - تحديات ممتعة", "اعتراف - اعترافات",
                                                "منشن - منشن اصدقائك", "اقتباس - اقتباسات ملهمة"]},
            {"title": "اوامر اللعب", "items": ["لمح - تلميح للاجابة", "جاوب - اظهار الجواب",
                                             "ايقاف - ايقاف اللعبة", "انسحب - الانسحاب من الدورة"]},
            {"title": "ملاحظات مهمة", "items": ["يجب التسجيل قبل اللعب",
                                               "النقاط تحفظ تلقائيا",
                                               "يمكن تغيير الثيم بين فاتح وداكن",
                                               "الالعاب متعددة اللاعبين في المجموعات"]}
        ]
        contents = [
            {"type": "text", "text": "دليل الاستخدام", "size": "xl", "weight": "bold",
             "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        for section in sections:
            contents.extend([
                {"type": "text", "text": section["title"], "size": "sm", "weight": "bold",
                 "color": c["text"], "margin": "lg"},
                {"type": "text", "text": "\n".join(section["items"]), "size": "xs",
                 "color": c["text2"], "wrap": True, "margin": "sm"}
            ])
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "horizontal", "margin": "md",
             "contents": [UI._btn("رجوع", "بداية", theme, "secondary")]}
        ])
        return {"type": "bubble", "size": "mega",
                "body": {"type": "box", "layout": "vertical",
                         "backgroundColor": c["bg"], "paddingAll": "20px",
                         "contents": contents}}

    @staticmethod
    def stats(user, theme="dark"):
        c = UI._c(theme)
        win_rate = int((user['wins'] / user['games'] * 100)) if user['games'] > 0 else 0
        return {
            "type": "bubble",
            "size": "mega",
            "body": {"type": "box", "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px",
                     "contents": [
                         {"type": "text", "text": "احصائياتك", "size": "xl", "weight": "bold",
                          "align": "center", "color": c["primary"]},
                         {"type": "separator", "margin": "md", "color": c["border"]},
                         {"type": "box", "layout": "vertical", "margin": "lg", "contents": [
                             {"type": "text", "text": user['name'], "size": "lg", "weight": "bold",
                              "color": c["text"], "align": "center"},
                             {"type": "text", "text": f"{user['points']} نقطة", "size": "xxl",
                              "weight": "bold", "color": c["success"], "align": "center", "margin": "sm"}
                         ], "backgroundColor": c["bg"], "cornerRadius": "12px", "paddingAll": "16px"},
                         {"type": "box", "layout": "horizontal", "margin": "lg", "contents": [
                             {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                                 {"type": "text", "text": "العاب", "size": "xs", "color": c["text2"], "align": "center"},
                                 {"type": "text", "text": str(user['games']), "size": "xl", "weight": "bold",
                                  "color": c["text"], "align": "center", "margin": "xs"}
                             ]},
                             {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                                 {"type": "text", "text": "فوز", "size": "xs", "color": c["text2"], "align": "center"},
                                 {"type": "text", "text": str(user['wins']), "size": "xl", "weight": "bold",
                                  "color": c["success"], "align": "center", "margin": "xs"}
                             ]},
                             {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                                 {"type": "text", "text": "نسبة", "size": "xs", "color": c["text2"], "align": "center"},
                                 {"type": "text", "text": f"{win_rate}%", "size": "xl", "weight": "bold",
                                  "color": c["accent"], "align": "center", "margin": "xs"}
                             ]}
                         ]},
                         {"type": "separator", "margin": "lg", "color": c["border"]},
                         {"type": "box", "layout": "horizontal", "margin": "md", "spacing": "xs",
                          "contents": [UI._btn("الصدارة", "الصدارة", theme),
                                       UI._btn("رجوع", "بداية", theme, "secondary")]}
                     ]}
        }

    @staticmethod
    def leaderboard(leaders, theme="dark"):
        c = UI._c(theme)
        contents = [
            {"type": "text", "text": "قائمة المتصدرين", "size": "xl", "weight": "bold",
             "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        if not leaders:
            contents.append({"type": "text", "text": "لا يوجد لاعبون بعد", "size": "sm",
                             "color": c["text2"], "align": "center", "margin": "lg"})
        else:
            for i, leader in enumerate(leaders[:10]):
                rank_colors = [c["success"], c["accent"], c["warning"]]
                rank_color = rank_colors[i] if i < 3 else c["text2"]
                contents.append({"type": "box", "layout": "horizontal",
                                 "contents": [
                                     {"type": "text", "text": f"#{i+1}", "size": "sm",
                                      "weight": "bold", "color": rank_color, "flex": 0},
                                     {"type": "text", "text": leader['name'], "size": "sm",
                                      "color": c["text"], "flex": 3, "margin": "md"},
                                     {"type": "text", "text": str(leader['points']), "size": "sm",
                                      "weight": "bold", "color": c["primary"], "align": "end", "flex": 1}
                                 ],
                                 "paddingAll": "8px", "margin": "sm", "backgroundColor": c["bg"], "cornerRadius": "8px" if i < 3 else "0px"})
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "horizontal", "margin": "md",
             "contents": [UI._btn("رجوع", "بداية", theme, "secondary")]}
        ])
        return {"type": "bubble", "size": "mega",
                "body": {"type": "box", "layout": "vertical",
                         "backgroundColor": c["bg"], "paddingAll": "20px", "contents": contents}}
