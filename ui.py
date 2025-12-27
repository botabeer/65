from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

class UI:
    THEMES = {
        "light": {
            "primary": "#1E293B", "text": "#334155", "text2": "#64748B",
            "text3": "#94A3B8", "bg": "#FFFFFF", "card": "#F8FAFC",
            "border": "#E2E8F0", "button": "#F1F5F9", "success": "#0EA5E9",
            "warning": "#F59E0B", "error": "#EF4444", "accent": "#3B82F6"
        },
        "dark": {
            "primary": "#F1F5F9", "text": "#CBD5E1", "text2": "#94A3B8",
            "text3": "#64748B", "bg": "#0F172A", "card": "#1E293B",
            "border": "#334155", "button": "#334155", "success": "#38BDF8",
            "warning": "#FBBF24", "error": "#F87171", "accent": "#60A5FA"
        }
    }

    @staticmethod
    def _c(theme):
        return UI.THEMES.get(theme, UI.THEMES["light"])

    @staticmethod
    def _button(label, text, c, style="secondary"):
        return {
            "type": "button", "style": style, "height": "sm",
            "action": {"type": "message", "label": label, "text": text},
            "color": c["button"] if style == "secondary" else c["primary"],
            "flex": 1
        }

    @staticmethod
    def get_quick_reply():
        actions = [
            ("بداية", "بداية"), ("العاب", "العاب"), ("نصوص", "نص"),
            ("نقاطي", "نقاطي"), ("صدارة", "الصدارة"), ("مساعدة", "مساعدة")
        ]
        return QuickReply(items=[
            QuickReplyItem(action=MessageAction(label=l, text=t))
            for l, t in actions
        ])

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
                    {"type": "text", "text": "يجب التسجيل للعب",
                     "size": "sm", "align": "center", "color": c["error"], "weight": "bold"},
                    {"type": "text", "text": "اكتب: تسجيل",
                     "size": "xs", "align": "center", "color": c["text3"], "margin": "xs"}
                ],
                "backgroundColor": c["card"], "paddingAll": "12px",
                "cornerRadius": "8px"
            })
        
        button_rows = [
            [("العاب", "العاب"), ("نصوص", "نص")],
            [("نقاطي", "نقاطي"), ("صدارة", "الصدارة")],
            [("تسجيل" if not registered else "تغيير", "تسجيل"), ("ثيم", "ثيم")]
        ]
        
        for row in button_rows:
            contents.append({
                "type": "box", "layout": "horizontal", "spacing": "xs",
                "margin": "sm" if row != button_rows[0] else "lg",
                "contents": [UI._button(l, t, c) for l, t in row]
            })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "text", "text": "تم انشاء البوت بواسطة عبير الدوسري - 2025",
             "size": "xxs", "color": c["text3"], "align": "center", "margin": "md"}
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
                "items": [
                    "بداية - القائمة الرئيسية",
                    "تسجيل - تسجيل اسمك",
                    "نقاطي - احصائياتك",
                    "الصدارة - قائمة المتصدرين"
                ]
            },
            {
                "title": "اوامر اللعب",
                "items": [
                    "لمح - تلميح للاجابة",
                    "جاوب - اظهار الجواب",
                    "ايقاف - ايقاف اللعبة",
                    "انسحب - الانسحاب"
                ]
            },
            {
                "title": "ملاحظات",
                "items": [
                    "يجب التسجيل للعب",
                    "النقاط تحفظ تلقائيا",
                    "يمكن تغيير الثيم"
                ]
            }
        ]
        
        contents = [
            {"type": "text", "text": "دليل الاستخدام", "size": "xl",
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        
        for section in sections:
            contents.append({
                "type": "text", "text": section["title"], "size": "sm",
                "weight": "bold", "color": c["text"], "margin": "lg"
            })
            contents.append({
                "type": "text", "text": "\n".join(section["items"]),
                "size": "xs", "color": c["text2"], "wrap": True, "margin": "sm"
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
    def text_menu(theme="light"):
        c = UI._c(theme)
        
        texts = [
            ("سؤال", "سؤال"), ("منشن", "منشن"), ("تحدي", "تحدي"),
            ("اعتراف", "اعتراف"), ("مجهول", "مجهول"), ("خاص", "خاص"),
            ("اقتباس", "اقتباس"), ("موقف", "موقف"), ("نصيحة", "نصيحة")
        ]
        
        contents = [
            {"type": "text", "text": "قائمة النصوص", "size": "xl",
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        
        for i in range(0, len(texts), 3):
            contents.append({
                "type": "box", "layout": "horizontal", "spacing": "xs",
                "margin": "sm" if i > 0 else "lg",
                "contents": [UI._button(l, t, c) for l, t in texts[i:i+3]]
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
    def games_menu(theme="light"):
        c = UI._c(theme)
        
        games = [
            ("خمن", "خمن"), ("سريع", "اسرع"), ("توافق", "توافق"),
            ("اغنية", "اغنيه"), ("ضد", "ضد"), ("سلسلة", "سلسله"),
            ("تكوين", "تكوين"), ("فئة", "فئه"), ("انسان", "لعبه"),
            ("ذكاء", "ذكاء"), ("ترتيب", "ترتيب"), ("حروف", "حروف"),
            ("سين", "سين"), ("لون", "لون"), ("روليت", "روليت")
        ]
        
        contents = [
            {"type": "text", "text": "قائمة الالعاب", "size": "xl",
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "text", "text": "اختر لعبة للبدء", "size": "xs",
             "color": c["text2"], "align": "center", "margin": "xs"},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        
        for i in range(0, len(games), 3):
            contents.append({
                "type": "box", "layout": "horizontal", "spacing": "xs",
                "margin": "sm" if i > 0 else "lg",
                "contents": [UI._button(l, t, c) for l, t in games[i:i+3]]
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
        
        return {
            "type": "bubble", "size": "mega",
            "body": {
                "type": "box", "layout": "vertical",
                "backgroundColor": c["bg"], "paddingAll": "20px",
                "contents": [
                    {"type": "text", "text": "احصائياتك", "size": "xl",
                     "weight": "bold", "align": "center", "color": c["primary"]},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "box", "layout": "vertical", "margin": "lg",
                        "contents": [
                            {"type": "text", "text": user['name'], "size": "lg",
                             "weight": "bold", "color": c["text"], "align": "center"},
                            {"type": "text", "text": f"{user['points']} نقطة", "size": "xxl",
                             "weight": "bold", "color": c["success"], "align": "center", "margin": "sm"}
                        ],
                        "backgroundColor": c["card"], "cornerRadius": "12px",
                        "paddingAll": "16px"
                    },
                    {
                        "type": "box", "layout": "horizontal", "margin": "lg",
                        "contents": [
                            {
                                "type": "box", "layout": "vertical", "flex": 1,
                                "contents": [
                                    {"type": "text", "text": "العاب", "size": "xs",
                                     "color": c["text2"], "align": "center"},
                                    {"type": "text", "text": str(user['games']), "size": "xl",
                                     "weight": "bold", "color": c["text"], "align": "center", "margin": "xs"}
                                ]
                            },
                            {
                                "type": "box", "layout": "vertical", "flex": 1,
                                "contents": [
                                    {"type": "text", "text": "فوز", "size": "xs",
                                     "color": c["text2"], "align": "center"},
                                    {"type": "text", "text": str(user['wins']), "size": "xl",
                                     "weight": "bold", "color": c["success"], "align": "center", "margin": "xs"}
                                ]
                            },
                            {
                                "type": "box", "layout": "vertical", "flex": 1,
                                "contents": [
                                    {"type": "text", "text": "نسبة", "size": "xs",
                                     "color": c["text2"], "align": "center"},
                                    {"type": "text", "text": f"{win_rate}%", "size": "xl",
                                     "weight": "bold", "color": c["accent"], "align": "center", "margin": "xs"}
                                ]
                            }
                        ]
                    },
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {
                        "type": "box", "layout": "horizontal", "margin": "md", "spacing": "xs",
                        "contents": [
                            UI._button("صدارة", "الصدارة", c),
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
            {"type": "text", "text": "قائمة المتصدرين", "size": "xl",
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        
        if not leaders:
            contents.append({
                "type": "text", "text": "لا يوجد لاعبون",
                "size": "sm", "color": c["text2"], "align": "center", "margin": "lg"
            })
        else:
            for i, leader in enumerate(leaders[:10]):
                rank_colors = [c["success"], c["accent"], c["warning"]]
                rank_color = rank_colors[i] if i < 3 else c["text2"]
                
                contents.append({
                    "type": "box", "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": f"#{i+1}", "size": "sm",
                         "weight": "bold", "color": rank_color, "flex": 0},
                        {"type": "text", "text": leader['name'], "size": "sm",
                         "color": c["text"], "flex": 3, "margin": "md"},
                        {"type": "text", "text": str(leader['points']), "size": "sm",
                         "weight": "bold", "color": c["primary"], "align": "end", "flex": 1}
                    ],
                    "paddingAll": "8px", "margin": "sm",
                    "backgroundColor": c["card"] if i < 3 else "transparent",
                    "cornerRadius": "8px" if i < 3 else "0px"
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
