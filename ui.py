from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

class UI:
    """واجهة مستخدم محسنة واحترافية"""

    THEMES = {
        "light": {
            "primary": "#000000",
            "text": "#1A1A1A",
            "text2": "#4D4D4D",
            "text3": "#808080",
            "bg": "#FFFFFF",
            "card": "#F5F5F5",
            "border": "#E0E0E0",
            "button": "#F5F5F5",
            "button_text": "#000000",
            "success": "#000000",
            "accent": "#4D4D4D",
            "warning": "#808080",
            "error": "#000000"
        },
        "dark": {
            "primary": "#FFFFFF",
            "text": "#E6E6E6",
            "text2": "#B3B3B3",
            "text3": "#808080",
            "bg": "#1A1A1A",
            "card": "#2D2D2D",
            "border": "#404040",
            "button": "#F5F5F5",
            "button_text": "#000000",
            "success": "#FFFFFF",
            "accent": "#B3B3B3",
            "warning": "#808080",
            "error": "#FFFFFF"
        }
    }

    @staticmethod
    def _c(theme):
        """الحصول على ألوان الثيم"""
        return UI.THEMES.get(theme, UI.THEMES["light"])

    @staticmethod
    def _btn(label, text, theme="light"):
        """إنشاء زر موحد"""
        c = UI._c(theme)
        return {
            "type": "button",
            "style": "secondary",
            "height": "sm",
            "action": {"type": "message", "label": label, "text": text},
            "color": c["button"]
        }

    @staticmethod
    def get_quick_reply():
        """قائمة الردود السريعة"""
        items = [
            ("بداية", "بداية"),
            ("العاب", "العاب"),
            ("نص", "نص"),
            ("نقاطي", "نقاطي"),
            ("الصدارة", "الصدارة"),
            ("مساعدة", "مساعدة")
        ]
        return QuickReply(
            items=[QuickReplyItem(action=MessageAction(label=l, text=t)) for l, t in items]
        )

    @staticmethod
    def welcome(name, registered, theme="light"):
        """شاشة الترحيب الرئيسية"""
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
                "margin": "sm"
            },
            {
                "type": "separator",
                "margin": "lg",
                "color": c["border"]
            }
        ]

        if not registered:
            contents.append({
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "backgroundColor": c["card"],
                "cornerRadius": "12px",
                "paddingAll": "16px",
                "borderWidth": "2px",
                "borderColor": c["error"],
                "contents": [
                    {
                        "type": "text",
                        "text": "يجب التسجيل للعب",
                        "size": "sm",
                        "weight": "bold",
                        "align": "center",
                        "color": c["error"]
                    },
                    {
                        "type": "text",
                        "text": "اكتب: تسجيل",
                        "size": "xs",
                        "align": "center",
                        "color": c["text3"],
                        "margin": "xs"
                    }
                ]
            })

        button_groups = [
            [("تسجيل", "تسجيل"), ("انسحب", "انسحب")],
            [("نقاطي", "نقاطي"), ("الصدارة", "الصدارة")],
            [("نص", "نص"), ("العاب", "العاب")],
            [("ثيم", "ثيم"), ("مساعدة", "مساعدة")]
        ]

        for group in button_groups:
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "margin": "sm" if group != button_groups[0] else "lg",
                "contents": [UI._btn(label, text, theme) for label, text in group]
            })

        contents.extend([
            {
                "type": "separator",
                "margin": "lg",
                "color": c["border"]
            },
            {
                "type": "text",
                "text": "تم إنشاء هذا البوت بواسطة عبير الدوسري 2025",
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
    def text_commands_menu(theme="light"):
        """قائمة الأوامر النصية"""
        c = UI._c(theme)
        
        commands = [
            ("سؤال", "سؤال"),
            ("منشن", "منشن"),
            ("تحدي", "تحدي"),
            ("اعتراف", "اعتراف"),
            ("مجهول", "مجهول"),
            ("خاص", "خاص"),
            ("نصيحة", "نصيحة"),
            ("موقف", "موقف"),
            ("اقتباس", "اقتباس")
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
                "text": "اختر نوع المحتوى",
                "size": "xs",
                "color": c["text2"],
                "align": "center",
                "margin": "xs"
            },
            {
                "type": "separator",
                "margin": "md",
                "color": c["border"]
            }
        ]

        for i in range(0, len(commands), 3):
            row = commands[i:i+3]
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "margin": "sm" if i > 0 else "lg",
                "contents": [UI._btn(label, text, theme) for label, text in row]
            })

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
                "contents": [UI._btn("رجوع", "بداية", theme)]
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
        """قائمة الألعاب"""
        c = UI._c(theme)
        
        games = [
            ("فئه", "فئه"),
            ("اسرع", "اسرع"),
            ("توافق", "توافق"),
            ("اغنيه", "اغنيه"),
            ("ضد", "ضد"),
            ("سلسله", "سلسله"),
            ("تكوين", "تكوين"),
            ("لغز", "لغز"),
            ("ترتيب", "ترتيب"),
            ("حرف", "حرف"),
            ("لون", "لون"),
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
                "text": "اختر لعبة للبدء",
                "size": "xs",
                "color": c["text2"],
                "align": "center",
                "margin": "xs"
            },
            {
                "type": "separator",
                "margin": "md",
                "color": c["border"]
            }
        ]

        for i in range(0, len(games), 3):
            row = games[i:i+3]
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "margin": "sm" if i > 0 else "lg",
                "contents": [UI._btn(label, text, theme) for label, text in row]
            })

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
                "contents": [UI._btn("رجوع", "بداية", theme)]
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
        """بطاقة المساعدة"""
        c = UI._c(theme)
        
        sections = [
            {
                "title": "الاوامر الاساسية",
                "items": [
                    "بداية - القائمة الرئيسية",
                    "تسجيل - تسجيل اسمك",
                    "نقاطي - احصائياتك",
                    "الصدارة - قائمة المتصدرين",
                    "ثيم - تغيير المظهر",
                    "انسحب - الخروج من اللعبة"
                ]
            },
            {
                "title": "اوامر النصوص",
                "items": [
                    "نص - قائمة النصوص",
                    "سؤال - اسئلة متنوعة",
                    "تحدي - تحديات ممتعة",
                    "منشن - منشن اصدقائك",
                    "اقتباس - اقتباسات ملهمة"
                ]
            },
            {
                "title": "اوامر اللعب",
                "items": [
                    "لمح - تلميح للاجابة",
                    "جاوب - اظهار الجواب",
                    "ايقاف - ايقاف اللعبة"
                ]
            },
            {
                "title": "ملاحظات مهمة",
                "items": [
                    "يجب التسجيل قبل اللعب",
                    "النقاط تحفظ تلقائيا",
                    "الالعاب متعددة اللاعبين"
                ]
            }
        ]

        contents = [
            {
                "type": "text",
                "text": "دليل الاستخدام",
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

        for section in sections:
            contents.extend([
                {
                    "type": "text",
                    "text": section["title"],
                    "size": "sm",
                    "weight": "bold",
                    "color": c["text"],
                    "margin": "lg"
                },
                {
                    "type": "text",
                    "text": "\n".join(section["items"]),
                    "size": "xs",
                    "color": c["text2"],
                    "wrap": True,
                    "margin": "sm"
                }
            ])

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
                "contents": [UI._btn("رجوع", "بداية", theme)]
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
        """احصائيات المستخدم"""
        c = UI._c(theme)
        
        win_rate = int((user['wins'] / user['games'] * 100)) if user['games'] > 0 else 0

        contents = [
            {
                "type": "text",
                "text": "احصائياتك",
                "size": "xl",
                "weight": "bold",
                "align": "center",
                "color": c["primary"]
            },
            {
                "type": "separator",
                "margin": "md",
                "color": c["border"]
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "backgroundColor": c["card"],
                "cornerRadius": "12px",
                "paddingAll": "16px",
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
                        "color": c["success"],
                        "align": "center",
                        "margin": "sm"
                    }
                ]
            },
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "lg",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "flex": 1,
                        "contents": [
                            {
                                "type": "text",
                                "text": "العاب",
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
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "flex": 1,
                        "contents": [
                            {
                                "type": "text",
                                "text": "فوز",
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
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "flex": 1,
                        "contents": [
                            {
                                "type": "text",
                                "text": "نسبة",
                                "size": "xs",
                                "color": c["text2"],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": f"{win_rate}%",
                                "size": "xl",
                                "weight": "bold",
                                "color": c["accent"],
                                "align": "center",
                                "margin": "xs"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "separator",
                "margin": "lg",
                "color": c["border"]
            },
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "spacing": "sm",
                "contents": [
                    UI._btn("الصدارة", "الصدارة", theme),
                    UI._btn("رجوع", "بداية", theme)
                ]
            }
        ]

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
    def leaderboard(leaders, theme="light"):
        """قائمة المتصدرين"""
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
            {
                "type": "separator",
                "margin": "md",
                "color": c["border"]
            }
        ]

        if not leaders:
            contents.append({
                "type": "text",
                "text": "لا يوجد لاعبون بعد",
                "size": "sm",
                "color": c["text2"],
                "align": "center",
                "margin": "lg"
            })
        else:
            for i, leader in enumerate(leaders[:10]):
                rank_colors = {0: c["success"], 1: c["accent"], 2: c["warning"]}
                rank_color = rank_colors.get(i, c["text2"])
                
                contents.append({
                    "type": "box",
                    "layout": "horizontal",
                    "backgroundColor": c["card"],
                    "cornerRadius": "8px",
                    "paddingAll": "12px",
                    "margin": "xs" if i > 0 else "lg",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"#{i+1}",
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
                            "margin": "md"
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
                    ]
                })

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
                "contents": [UI._btn("رجوع", "بداية", theme)]
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
