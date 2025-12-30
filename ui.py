from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction, FlexContainer, FlexMessage

class UI:
    """واجهة مستخدم رسمية للبوت، كامل نوافذ فلكس، أزرار موحدة، ثيم فاتح وداكن"""

    THEMES = {
        "light": {
            "primary": "#000000",       # أسود - عناوين رئيسية
            "secondary": "#333333",     # رمادي غامق - عناوين فرعية
            "text": "#000000",          # أسود - نصوص عامة
            "text2": "#555555",         # رمادي متوسط - نصوص ثانوية
            "text3": "#777777",         # رمادي فاتح - وصف/مساعدة
            "bg": "#FFFFFF",            # أبيض - خلفية عامة
            "card": "#F5F5F5",          # رمادي فاتح جداً - بطاقات
            "border": "#DDDDDD",        # رمادي فاتح - فواصل
            "button": "#F5F5F5",        # موحد لكل الأزرار
            "button_text": "#000000",   # نص الأزرار أسود
            "accent": "#1E40AF"         # أزرق رسمي لتسليط الضوء
        },
        "dark": {
            "primary": "#FFFFFF",       # أبيض - عناوين رئيسية
            "secondary": "#CCCCCC",     # رمادي فاتح - عناوين فرعية
            "text": "#FFFFFF",          # أبيض - نصوص عامة
            "text2": "#AAAAAA",         # رمادي متوسط
            "text3": "#888888",         # رمادي غامق
            "bg": "#0F172A",            # أزرق غامق قريب من الأسود
            "card": "#1E293B",          # أزرق غامق للبطاقات
            "border": "#334155",        # فواصل رمادية غامقة
            "button": "#F5F5F5",        # موحد لكل الأزرار
            "button_text": "#000000",   # نص الأزرار أسود
            "accent": "#1E40AF"         # أزرق رسمي
        }
    }

    @staticmethod
    def _c(theme="light"):
        return UI.THEMES.get(theme, UI.THEMES["light"])

    @staticmethod
    def _btn(label, text, theme="light"):
        colors = UI._c(theme)
        return {
            "type": "button",
            "style": "primary",
            "height": "sm",
            "action": {"type": "message", "label": label, "text": text},
            "color": colors["button"],
            "flex": 1,
            "text_color": colors["button_text"]
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
    def welcome(name, registered, theme="light"):
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
                     "align": "center", "color": c["text3"], "weight": "bold"},
                    {"type": "text", "text": "اكتب: تسجيل", "size": "xs",
                     "align": "center", "color": c["text3"], "margin": "xs"}
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "12px", "cornerRadius": "8px"
            })
        # أزرار الترحيب
        contents.extend([
            {"type": "box", "layout": "horizontal", "spacing": "xs", "margin": "lg",
             "contents": [UI._btn("تسجيل", "تسجيل", theme),
                          UI._btn("انسحب", "انسحب", theme)]},
            {"type": "box", "layout": "horizontal", "spacing": "xs", "margin": "sm",
             "contents": [UI._btn("نقاطي", "نقاطي", theme),
                          UI._btn("الصدارة", "الصدارة", theme)]},
            {"type": "box", "layout": "horizontal", "spacing": "xs", "margin": "sm",
             "contents": [UI._btn("نص", "نص", theme), UI._btn("العاب", "العاب", theme)]},
            {"type": "box", "layout": "horizontal", "spacing": "xs", "margin": "sm",
             "contents": [UI._btn("ثيم", "ثيم", theme), UI._btn("مساعدة", "مساعدة", theme)]},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "text", "text": "تم إنشاء هذا البوت بواسطة عبير الدوسري @ 2025",
             "size": "xxs", "color": c["text3"], "align": "center", "margin": "md"}
        ])
        bubble = {"type": "bubble", "size": "mega", "body": {"type": "box",
                 "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px",
                 "contents": contents}}
        return FlexMessage(alt_text="مرحباً", contents=FlexContainer.from_dict(bubble))

    @staticmethod
    def menu(title, buttons, theme="light"):
        c = UI._c(theme)
        contents = [
            {"type": "text", "text": title, "size": "xl", "weight": "bold",
             "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        for i in range(0, len(buttons), 3):
            row = [UI._btn(label, text, theme) for label, text in buttons[i:i+3]]
            contents.append({"type": "box", "layout": "horizontal", "spacing": "xs",
                             "margin": "sm" if i > 0 else "lg",
                             "contents": row})
        contents.append({"type": "separator", "margin": "lg", "color": c["border"]})
        contents.append({"type": "box", "layout": "horizontal", "margin": "md",
                         "contents": [UI._btn("رجوع", "بداية", theme)]})
        bubble = {"type": "bubble", "size": "mega", "body": {"type": "box",
                 "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px",
                 "contents": contents}}
        return FlexMessage(alt_text=title, contents=FlexContainer.from_dict(bubble))

    @staticmethod
    def text_commands_menu(theme="light"):
        commands = [("سؤال", "سؤال"), ("منشن", "منشن"), ("تحدي", "تحدي"),
                    ("اعتراف", "اعتراف"), ("مجهول", "مجهول"), ("خاص", "خاص"),
                    ("نصيحة", "نصيحة"), ("موقف", "موقف"), ("اقتباس", "اقتباس")]
        return UI.menu("قائمة النصوص", commands, theme)

    @staticmethod
    def games_menu(theme="light"):
        games = [("فئة", "فئة"), ("اسرع", "اسرع"), ("توافق", "توافق"),
                 ("اغنية", "اغنية"), ("ضد", "ضد"), ("سلسله", "سلسله"),
                 ("تكوين", "تكوين"), ("لغز", "لغز"), ("ترتيب", "ترتيب"),
                 ("حرف", "حرف"), ("لون", "لون"), ("مافيا", "مافيا")]
        return UI.menu("قائمة الألعاب", games, theme)

    @staticmethod
    def help_card(theme="light"):
        c = UI._c(theme)
        sections = [
            {"title": "الأوامر الأساسية", "items": [
                "بداية - القائمة الرئيسية",
                "تسجيل - تسجيل اسمك",
                "نقاطي - احصائياتك",
                "الصدارة - قائمة المتصدرين",
                "ثيم - تغيير المظهر",
                "انسحب - الخروج من اللعبة"]},
            {"title": "أوامر النصوص", "items": [
                "نص - قائمة النصوص", "سؤال - اسئلة متنوعة",
                "تحدي - تحديات ممتعة", "اعتراف - اعترافات",
                "منشن - منشن أصدقائك", "اقتباس - اقتباسات ملهمة"]},
            {"title": "أوامر اللعب", "items": [
                "لمح - تلميح للإجابة", "جاوب - اظهار الجواب",
                "ايقاف - ايقاف اللعبة", "انسحب - الانسحاب من الدورة"]},
            {"title": "ملاحظات مهمة", "items": [
                "يجب التسجيل قبل اللعب",
                "النقاط تحفظ تلقائياً",
                "يمكن تغيير الثيم بين فاتح وداكن",
                "الألعاب متعددة اللاعبين في المجموعات"]}
        ]
        contents = [
            {"type": "text", "text": "دليل الاستخدام", "size": "xl", "weight": "bold",
             "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        for section in sections:
            contents.append({"type": "text", "text": section["title"], "size": "sm", "weight": "bold",
                             "color": c["text"], "margin": "lg"})
            contents.append({"type": "text", "text": "\n".join(section["items"]), "size": "xs",
                             "color": c["text2"], "wrap": True, "margin": "sm"})
        contents.append({"type": "separator", "margin": "lg", "color": c["border"]})
        contents.append({"type": "box", "layout": "horizontal", "margin": "md",
                         "contents": [UI._btn("رجوع", "بداية", theme)]})
        bubble = {"type": "bubble", "size": "mega", "body": {"type": "box",
                 "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px",
                 "contents": contents}}
        return FlexMessage(alt_text="دليل الاستخدام", contents=FlexContainer.from_dict(bubble))

    @staticmethod
    def stats(user, theme="light"):
        c = UI._c(theme)
        win_rate = int(user['wins']/user['games']*100) if user['games'] > 0 else 0
        contents = [
            {"type": "text", "text": "إحصائياتك", "size": "xl", "weight": "bold",
             "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {"type": "box", "layout": "vertical", "margin": "lg",
             "contents": [
                 {"type": "text", "text": user['name'], "size": "lg", "weight": "bold",
                  "color": c["text"], "align": "center"},
                 {"type": "text", "text": f"{user['points']} نقطة", "size": "xxl",
                  "weight": "bold", "color": c["accent"], "align": "center", "margin": "sm"}
             ], "backgroundColor": c["card"], "cornerRadius": "12px", "paddingAll": "16px"},
            {"type": "box", "layout": "horizontal", "margin": "lg",
             "contents": [
                 {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                     {"type": "text", "text": "الألعاب", "size": "xs", "color": c["text2"], "align": "center"},
                     {"type": "text", "text": str(user['games']), "size": "xl", "weight": "bold",
                      "color": c["text"], "align": "center", "margin": "xs"}
                 ]},
                 {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                     {"type": "text", "text": "فوز", "size": "xs", "color": c["text2"], "align": "center"},
                     {"type": "text", "text": str(user['wins']), "size": "xl", "weight": "bold",
                      "color": c["accent"], "align": "center", "margin": "xs"}
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
                          UI._btn("رجوع", "بداية", theme)]}
        ]
        bubble = {"type": "bubble", "size": "mega", "body": {"type": "box",
                 "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px",
                 "contents": contents}}
        return FlexMessage(alt_text="إحصائياتك", contents=FlexContainer.from_dict(bubble))

    @staticmethod
    def leaderboard(leaders, theme="light"):
        c = UI._c(theme)
        contents = [{"type": "text", "text": "المتصدرين", "size": "xl", "weight": "bold",
                     "align": "center", "color": c["primary"]},
                    {"type": "separator", "margin": "md", "color": c["border"]}]
        if not leaders:
            contents.append({"type": "text", "text": "لا يوجد لاعبون بعد", "size": "sm",
                             "color": c["text2"], "align": "center", "margin": "lg"})
        else:
            for i, leader in enumerate(leaders[:10]):
                contents.append({"type": "box", "layout": "horizontal",
                                 "contents": [
                                     {"type": "text", "text": f"#{i+1}", "size": "sm",
                                      "weight": "bold", "color": c["accent"] if i<3 else c["text2"], "flex": 0},
                                     {"type": "text", "text": leader['name'], "size": "sm",
                                      "color": c["text"], "flex": 3, "margin": "md"},
                                     {"type": "text", "text": str(leader['points']), "size": "sm",
                                      "weight": "bold", "color": c["primary"], "align": "end", "flex": 1}
                                 ],
                                 "paddingAll": "8px", "margin": "sm", "backgroundColor": c["card"], "cornerRadius": "8px" if i<3 else "0px"})
        contents.append({"type": "separator", "margin": "lg", "color": c["border"]})
        contents.append({"type": "box", "layout": "horizontal", "margin": "md",
                         "contents": [UI._btn("رجوع", "بداية", theme)]})
        bubble = {"type": "bubble", "size": "mega", "body": {"type": "box",
                 "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px",
                 "contents": contents}}
        return FlexMessage(alt_text="المتصدرين", contents=FlexContainer.from_dict(bubble))
