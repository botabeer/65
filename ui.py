from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

class UI:
    BUTTON_COLOR = "#F8FBFC"
    
    THEMES = {
        "light": {
            "primary": "#2C3E50", "text": "#34495E", "text2": "#7F8C8D",
            "text3": "#95A5A6", "bg": "#FFFFFF", "card": "#F8F9FA",
            "border": "#E9ECEF", "button": "#F2F2F7", "success": "#27AE60",
            "warning": "#F39C12", "error": "#E74C3C", "accent": "#3498DB"
        },
        "dark": {
            "primary": "#ECF0F1", "text": "#BDC3C7", "text2": "#95A5A6",
            "text3": "#7F8C8D", "bg": "#1C2833", "card": "#273746",
            "border": "#34495E", "button": "#F2F2F7", "success": "#27AE60",
            "warning": "#F39C12", "error": "#E74C3C", "accent": "#3498DB"
        }
    }

    @staticmethod
    def _c(theme):
        return UI.THEMES.get(theme, UI.THEMES["light"])

    @staticmethod
    def _btn(label, text, c=None, style="secondary"):
        return {
            "type": "button", "style": style, "height": "sm",
            "action": {"type": "message", "label": label, "text": text},
            "color": UI.BUTTON_COLOR, "flex": 1
        }

    @staticmethod
    def get_quick_reply():
        items = [
            ("بداية", "بداية"), ("العاب", "العاب"), ("سؤال", "سؤال"),
            ("منشن", "منشن"), ("تحدي", "تحدي"), ("اعتراف", "اعتراف"),
            ("مجهول", "مجهول"), ("خاص", "خاص"), ("اقتباس", "اقتباس"),
            ("موقف", "موقف"), ("نصيحة", "نصيحة"), ("مساعدة", "مساعدة")
        ]
        return QuickReply(items=[QuickReplyItem(action=MessageAction(label=l, text=t)) for l, t in items])

    @staticmethod
    def welcome(name, registered, theme="light"):
        c = UI._c(theme)
        contents = [
            {"type": "text", "text": "Bot 65", "size": "xxl", "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "text", "text": f"مرحبا {name}", "size": "md", "align": "center", "color": c["text2"], "margin": "xs"},
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        if not registered:
            contents.append({
                "type": "box", "layout": "vertical", "margin": "lg",
                "contents": [
                    {"type": "text", "text": "يجب التسجيل للعب", "size": "sm", "align": "center", "color": c["error"], "weight": "bold"},
                    {"type": "text", "text": "اكتب تسجيل", "size": "xs", "align": "center", "color": c["text3"], "margin": "xs"}
                ],
                "backgroundColor": c["card"], "paddingAll": "12px", "cornerRadius": "8px"
            })
        
        # السطر الاول: تسجيل - انسحب
        contents.append({
            "type": "box", "layout": "horizontal", "spacing": "xs", "margin": "lg",
            "contents": [
                UI._btn("تسجيل", "تسجيل"),
                UI._btn("انسحب", "انسحب")
            ]
        })
        
        # السطر الثاني: نقاطي - الصدارة
        contents.append({
            "type": "box", "layout": "horizontal", "spacing": "xs", "margin": "sm",
            "contents": [
                UI._btn("نقاطي", "نقاطي"),
                UI._btn("الصدارة", "الصدارة")
            ]
        })
        
        # السطر الثالث: نص - العاب
        contents.append({
            "type": "box", "layout": "horizontal", "spacing": "xs", "margin": "sm",
            "contents": [
                UI._btn("نص", "نص"),
                UI._btn("العاب", "العاب")
            ]
        })
        
        # السطر الرابع: ثيم - مساعدة
        contents.append({
            "type": "box", "layout": "horizontal", "spacing": "xs", "margin": "sm",
            "contents": [
                UI._btn("ثيم", "ثيم"),
                UI._btn("مساعدة", "مساعدة")
            ]
        })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "text", "text": "تم انشاء هذا البوت بواسطة عبير الدوسري 2025", "size": "xxs", "color": c["text3"], "align": "center", "margin": "md"}
        ])
        
        return {
            "type": "bubble", "size": "mega",
            "body": {"type": "box", "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px", "contents": contents}
        }

    @staticmethod
    def text_commands_menu(theme="light"):
        c = UI._c(theme)
        
        commands = [
            ("سؤال", "سؤال"), ("منشن", "منشن"), ("تحدي", "تحدي"),
            ("اعتراف", "اعتراف"), ("مجهول", "مجهول"), ("خاص", "خاص"),
            ("نصيحة", "نصيحة"), ("موقف", "موقف"), ("اقتباس", "اقتباس")
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
                "type": "separator",
                "margin": "md",
                "color": c["border"]
            }
        ]
        
        # اضافة الازرار في صفوف (3 ازرار في كل صف)
        for i in range(0, len(commands), 3):
            row_buttons = []
            for label, text in commands[i:i+3]:
                row_buttons.append(UI._btn(label, text))
            
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "xs",
                "margin": "sm" if i > 0 else "lg",
                "contents": row_buttons
            })
        
        # زر الرجوع
        contents.extend([
            {
                "type": "separator",
                "margin": "lg",
                "color": c["border"]
            },
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": [UI._btn("رجوع", "بداية")]
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
        sections = [
            {"title": "الاوامر الاساسية", "items": ["بداية - القائمة الرئيسية", "تسجيل - تسجيل اسمك", "نقاطي - احصائياتك", "الصدارة - قائمة المتصدرين", "ثيم - تغيير المظهر", "انسحب - الخروج من اللعبة"]},
            {"title": "اوامر النصوص", "items": ["نص - قائمة النصوص", "سؤال - اسئلة متنوعة", "تحدي - تحديات", "اعتراف - اعترافات", "منشن - منشن اصدقائك", "اقتباس - اقتباسات ملهمة", "نصيحة - نصائح يومية", "مجهول - رسائل مجهولة", "خاص - رسائل خاصة", "شعر - قصائد", "موقف - مواقف"]},
            {"title": "اوامر اللعب", "items": ["لمح - تلميح للاجابة", "جاوب - اظهار الجواب", "ايقاف - ايقاف اللعبة", "انسحب - الانسحاب من الدورة"]},
            {"title": "ملاحظات مهمة", "items": ["يجب التسجيل قبل اللعب", "النقاط تحفظ تلقائيا", "يمكن تغيير الثيم بين فاتح وداكن", "الالعاب متعددة اللاعبين في المجموعات"]}
        ]
        
        contents = [
            {"type": "text", "text": "دليل الاستخدام", "size": "xl", "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        
        for section in sections:
            contents.append({"type": "text", "text": section["title"], "size": "sm", "weight": "bold", "color": c["text"], "margin": "lg"})
            contents.append({"type": "text", "text": "\n".join(section["items"]), "size": "xs", "color": c["text2"], "wrap": True, "margin": "sm"})
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "horizontal", "margin": "md", "contents": [UI._btn("رجوع", "بداية")]}
        ])
        
        return {
            "type": "bubble", "size": "mega",
            "body": {"type": "box", "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px", "contents": contents}
        }

    @staticmethod
    def games_menu(theme="light"):
        c = UI._c(theme)
        # بدون روليت
        games = [
            ("فئه", "فئه"), ("اسرع", "اسرع"), ("توافق", "توافق"),
            ("اغنيه", "اغنيه"), ("ضد", "ضد"), ("سلسله", "سلسله"),
            ("تكوين", "تكوين"), ("لغز", "لغز"), ("ترتيب", "ترتيب"),
            ("حرف", "حرف"), ("لون", "لون"), ("مافيا", "مافيا")
        ]
        
        contents = [
            {"type": "text", "text": "قائمة الالعاب", "size": "xl", "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "text", "text": "اختر لعبة للبدء", "size": "xs", "color": c["text2"], "align": "center", "margin": "xs"},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        
        for i in range(0, len(games), 3):
            contents.append({
                "type": "box", "layout": "horizontal", "spacing": "xs",
                "margin": "sm" if i > 0 else "lg",
                "contents": [UI._btn(l, t) for l, t in games[i:i+3]]
            })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "horizontal", "margin": "md", "contents": [UI._btn("رجوع", "بداية")]}
        ])
        
        return {
            "type": "bubble", "size": "mega",
            "body": {"type": "box", "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px", "contents": contents}
        }

    @staticmethod
    def stats(user, theme="light"):
        c = UI._c(theme)
        win_rate = int((user['wins'] / user['games'] * 100)) if user['games'] > 0 else 0
        
        return {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px",
                "contents": [
                    {"type": "text", "text": "احصائياتك", "size": "xl", "weight": "bold", "align": "center", "color": c["primary"]},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "box", "layout": "vertical", "margin": "lg",
                        "contents": [
                            {"type": "text", "text": user['name'], "size": "lg", "weight": "bold", "color": c["text"], "align": "center"},
                            {"type": "text", "text": f"{user['points']} نقطة", "size": "xxl", "weight": "bold", "color": c["success"], "align": "center", "margin": "sm"}
                        ],
                        "backgroundColor": c["card"], "cornerRadius": "12px", "paddingAll": "16px"
                    },
                    {
                        "type": "box", "layout": "horizontal", "margin": "lg",
                        "contents": [
                            {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                                {"type": "text", "text": "العاب", "size": "xs", "color": c["text2"], "align": "center"},
                                {"type": "text", "text": str(user['games']), "size": "xl", "weight": "bold", "color": c["text"], "align": "center", "margin": "xs"}
                            ]},
                            {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                                {"type": "text", "text": "فوز", "size": "xs", "color": c["text2"], "align": "center"},
                                {"type": "text", "text": str(user['wins']), "size": "xl", "weight": "bold", "color": c["success"], "align": "center", "margin": "xs"}
                            ]},
                            {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                                {"type": "text", "text": "نسبة", "size": "xs", "color": c["text2"], "align": "center"},
                                {"type": "text", "text": f"{win_rate}%", "size": "xl", "weight": "bold", "color": c["accent"], "align": "center", "margin": "xs"}
                            ]}
                        ]
                    },
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {"type": "box", "layout": "horizontal", "margin": "md", "spacing": "xs",
                     "contents": [UI._btn("الصدارة", "الصدارة"), UI._btn("رجوع", "بداية")]}
                ]
            }
        }

    @staticmethod
    def leaderboard(leaders, theme="light"):
        c = UI._c(theme)
        contents = [
            {"type": "text", "text": "قائمة المتصدرين", "size": "xl", "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        
        if not leaders:
            contents.append({"type": "text", "text": "لا يوجد لاعبون بعد", "size": "sm", "color": c["text2"], "align": "center", "margin": "lg"})
        else:
            for i, leader in enumerate(leaders[:10]):
                rank_colors = [c["success"], c["accent"], c["warning"]]
                rank_color = rank_colors[i] if i < 3 else c["text2"]
                
                contents.append({
                    "type": "box", "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": f"#{i+1}", "size": "sm", "weight": "bold", "color": rank_color, "flex": 0},
                        {"type": "text", "text": leader['name'], "size": "sm", "color": c["text"], "flex": 3, "margin": "md"},
                        {"type": "text", "text": str(leader['points']), "size": "sm", "weight": "bold", "color": c["primary"], "align": "end", "flex": 1}
                    ],
                    "paddingAll": "8px", "margin": "sm",
                    "backgroundColor": c["card"] if i < 3 else "transparent",
                    "cornerRadius": "8px" if i < 3 else "0px"
                })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "horizontal", "margin": "md", "contents": [UI._btn("رجوع", "بداية")]}
        ])
        
        return {
            "type": "bubble", "size": "mega",
            "body": {"type": "box", "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px", "contents": contents}
        }
