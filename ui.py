"""Bot 65 - UI Module - تصميم أنيق ومريح"""

from constants import GAME_LABELS


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
            "button": "#2D2D2D"
        },
        "dark": {
            "primary": "#F9FAFB",
            "text": "#E5E7EB",
            "text2": "#9CA3AF",
            "text3": "#6B7280",
            "bg": "#111827",
            "card": "#1F2937",
            "border": "#374151",
            "button": "#F9FAFB"
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
                "paddingAll": "24px",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "Bot 65",
                        "size": "xxl",
                        "weight": "bold",
                        "align": "center",
                        "color": c["primary"]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "xs",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"مرحباً {name}",
                                "size": "lg",
                                "align": "center",
                                "color": c["text"]
                            },
                            {
                                "type": "text",
                                "text": "مسجل" if registered else "غير مسجل",
                                "size": "xs",
                                "align": "center",
                                "color": c["text3"]
                            }
                        ]
                    },
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    UI._create_menu_section("الحساب", [
                        ("تسجيل" if not registered else "تغيير الاسم", "تسجيل"),
                        ("إحصائياتي", "نقاطي"),
                        ("المتصدرين", "الصدارة")
                    ], c),
                    UI._create_menu_section("الألعاب والأوامر", [
                        ("الألعاب", "العاب"),
                        ("المساعدة", "مساعدة"),
                        ("تغيير الثيم", "ثيم")
                    ], c),
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {
                        "type": "text",
                        "text": "عبير الدوسري 2025",
                        "size": "xxs",
                        "align": "center",
                        "color": c["text3"],
                        "margin": "sm"
                    }
                ]
            }
        }

    @staticmethod
    def _create_menu_section(title, buttons, c):
        contents = [
            {
                "type": "text",
                "text": title,
                "size": "sm",
                "weight": "bold",
                "color": c["text2"],
                "margin": "lg"
            }
        ]
        
        for label, text in buttons:
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "margin": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {"type": "message", "label": label, "text": text},
                        "color": c["text2"]
                    }
                ]
            })
        
        return {
            "type": "box",
            "layout": "vertical",
            "contents": contents
        }

    @staticmethod
    def games_menu(theme="light"):
        c = UI._c(theme)
        
        game_grid = [
            ["خمن", "اسرع", "اغنيه"],
            ["ضد", "تكوين", "فئه"],
            ["ذكاء", "ترتيب", "لون"],
            ["روليت", "سين", "سلسله"],
            ["لعبه", "حروف", "توافق"]
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
            {
                "type": "text",
                "text": "اختر لعبتك المفضلة",
                "size": "xs",
                "align": "center",
                "color": c["text3"],
                "margin": "sm"
            },
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        for row in game_grid:
            row_contents = []
            for game in row:
                row_contents.append({
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {"type": "message", "label": GAME_LABELS[game], "text": game},
                    "color": c["text2"],
                    "flex": 1
                })
            
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "margin": "sm",
                "contents": row_contents
            })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "text",
                "text": "للخروج اكتب: ايقاف",
                "size": "xxs",
                "align": "center",
                "color": c["text3"],
                "margin": "md"
            },
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": [
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {"type": "message", "label": "رجوع", "text": "بداية"},
                        "color": c["text2"]
                    }
                ]
            }
        ])
        
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
        
        sections = [
            {
                "title": "الأوامر الأساسية",
                "items": [
                    "بداية - الصفحة الرئيسية",
                    "تسجيل - تسجيل أو تغيير الاسم",
                    "العاب - قائمة الألعاب",
                    "نقاطي - عرض إحصائياتك",
                    "الصدارة - المتصدرين"
                ]
            },
            {
                "title": "أوامر اللعب",
                "items": [
                    "لمح - الحصول على تلميح",
                    "جاوب - إظهار الإجابة",
                    "ايقاف - إنهاء اللعبة",
                    "صعوبة 1-5 - تغيير المستوى"
                ]
            },
            {
                "title": "الأوامر النصية",
                "items": [
                    "سؤال - تحدي - اعتراف",
                    "منشن - حكمة - موقف"
                ]
            }
        ]
        
        contents = [
            {
                "type": "text",
                "text": "المساعدة",
                "size": "xl",
                "weight": "bold",
                "align": "center",
                "color": c["primary"]
            },
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        for section in sections:
            contents.append({
                "type": "text",
                "text": section["title"],
                "size": "md",
                "weight": "bold",
                "color": c["text"],
                "margin": "lg"
            })
            
            for item in section["items"]:
                contents.append({
                    "type": "text",
                    "text": item,
                    "size": "sm",
                    "color": c["text2"],
                    "margin": "sm",
                    "wrap": True
                })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": [
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {"type": "message", "label": "رجوع", "text": "بداية"},
                        "color": c["text2"]
                    }
                ]
            }
        ])
        
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
    def stats(user, theme="light"):
        c = UI._c(theme)
        win_rate = int((user['wins'] / user['games'] * 100)) if user['games'] > 0 else 0
        
        stats_items = [
            {"label": "النقاط", "value": str(user['points']), "highlight": True},
            {"label": "عدد الألعاب", "value": str(user['games'])},
            {"label": "الانتصارات", "value": str(user['wins'])},
            {"label": "نسبة الفوز", "value": f"{win_rate}%"}
        ]
        
        stats_contents = []
        for i, item in enumerate(stats_items):
            if i > 0:
                stats_contents.append({"type": "separator", "margin": "md", "color": c["border"]})
            
            stats_contents.append({
                "type": "box",
                "layout": "horizontal",
                "margin": "md" if i > 0 else "none",
                "contents": [
                    {
                        "type": "text",
                        "text": item["label"],
                        "size": "sm",
                        "color": c["text2"],
                        "flex": 1
                    },
                    {
                        "type": "text",
                        "text": item["value"],
                        "size": "xl" if item.get("highlight") else "md",
                        "weight": "bold",
                        "color": c["primary"] if item.get("highlight") else c["text"],
                        "align": "end",
                        "flex": 0
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
                "contents": [
                    {
                        "type": "text",
                        "text": "إحصائياتك",
                        "size": "xl",
                        "weight": "bold",
                        "align": "center",
                        "color": c["primary"]
                    },
                    {
                        "type": "text",
                        "text": user['name'],
                        "size": "md",
                        "align": "center",
                        "color": c["text2"],
                        "margin": "sm"
                    },
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": c["card"],
                        "cornerRadius": "8px",
                        "paddingAll": "16px",
                        "margin": "md",
                        "contents": stats_contents
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "button",
                                "style": "secondary",
                                "height": "sm",
                                "action": {"type": "message", "label": "رجوع", "text": "بداية"},
                                "color": c["text2"]
                            }
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
                "text": "المتصدرين",
                "size": "xl",
                "weight": "bold",
                "align": "center",
                "color": c["primary"]
            },
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        for i, leader in enumerate(leaders[:10]):
            rank_style = {
                0: {"size": "md", "weight": "bold"},
                1: {"size": "sm", "weight": "bold"},
                2: {"size": "sm", "weight": "bold"}
            }.get(i, {"size": "sm", "weight": "regular"})
            
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "margin": "md" if i == 0 else "sm",
                "paddingAll": "8px" if i < 3 else "4px",
                "backgroundColor": c["card"] if i < 3 else "none",
                "cornerRadius": "8px" if i < 3 else "none",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{i + 1}.",
                        "size": rank_style["size"],
                        "weight": rank_style["weight"],
                        "color": c["primary"] if i < 3 else c["text3"],
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": leader['name'],
                        "size": rank_style["size"],
                        "color": c["text"],
                        "flex": 3,
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": str(leader['points']),
                        "size": rank_style["size"],
                        "weight": rank_style["weight"],
                        "color": c["primary"] if i < 3 else c["text2"],
                        "align": "end",
                        "flex": 1
                    }
                ]
            })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": [
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {"type": "message", "label": "رجوع", "text": "بداية"},
                        "color": c["text2"]
                    }
                ]
            }
        ])
        
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
