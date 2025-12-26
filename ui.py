"""Bot 65 - UI Module - تصميم أنيق واحترافي"""

from constants import GAME_LABELS

class UI:
    THEMES = {
        "light": {
            "primary": "#000000",
            "text": "#1A1A1A",
            "text2": "#6B7280",
            "text3": "#9CA3AF",
            "bg": "#FFFFFF",
            "card": "#F8F9FA",
            "border": "#E5E7EB",
            "success": "#059669",
            "warning": "#D97706",
            "error": "#DC2626"
        },
        "dark": {
            "primary": "#FFFFFF",
            "text": "#F9FAFB",
            "text2": "#D1D5DB",
            "text3": "#9CA3AF",
            "bg": "#0F172A",
            "card": "#1E293B",
            "border": "#334155",
            "success": "#10B981",
            "warning": "#F59E0B",
            "error": "#EF4444"
        }
    }

    @staticmethod
    def _c(theme):
        return UI.THEMES.get(theme, UI.THEMES["light"])
    
    @staticmethod
    def _button(label, text, style="secondary", color=None, c=None):
        """إنشاء زر موحد"""
        if c is None:
            c = UI._c("light")
        if color is None:
            color = c["text2"]
        
        return {
            "type": "button",
            "style": style,
            "height": "sm",
            "action": {"type": "message", "label": label, "text": text},
            "color": color
        }

    @staticmethod
    def welcome(name, registered, theme="light"):
        c = UI._c(theme)
        
        status_box = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "الحالة", 
                         "size": "xxs", "color": c["text3"]},
                        {"type": "text", "text": "مسجل" if registered else "ضيف", 
                         "size": "sm", "weight": "bold", 
                         "color": c["success"] if registered else c["warning"]}
                    ],
                    "flex": 1
                }
            ],
            "backgroundColor": c["card"],
            "paddingAll": "12px",
            "cornerRadius": "8px",
            "margin": "md"
        }
        
        contents = [
            {"type": "text", "text": "Bot 65", "size": "xxl", 
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "text", "text": f"مرحباً {name}", "size": "lg", 
             "align": "center", "color": c["text"], "margin": "sm"},
            status_box,
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        quick_actions = [
            ("الألعاب", "العاب", c["primary"]),
            ("إحصائياتي" if registered else "تسجيل", "نقاطي" if registered else "تسجيل", c["text2"]),
            ("المتصدرين", "الصدارة", c["text2"])
        ]
        
        for label, text, color in quick_actions:
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "margin": "sm",
                "contents": [UI._button(label, text, "secondary", color, c)]
            })
        
        contents.extend([
            {"type": "separator", "margin": "md", "color": c["border"]},
            {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "margin": "sm",
                "contents": [
                    UI._button("مساعدة", "مساعدة", "secondary", c["text3"], c),
                    UI._button(f"ثيم {'داكن' if theme == 'light' else 'فاتح'}", "ثيم", "secondary", c["text3"], c)
                ]
            },
            {"type": "text", "text": "عبير الدوسري 2025", 
             "size": "xxs", "align": "center", "color": c["text3"], "margin": "md"}
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
            {"type": "text", "text": "قائمة الألعاب", "size": "xl", 
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "text", "text": "اختر لعبتك المفضلة", 
             "size": "xs", "align": "center", "color": c["text3"], "margin": "sm"},
            {"type": "separator", "margin": "md", "color": c["border"]}
        ]
        
        for i in range(0, len(games), 3):
            row_games = games[i:i+3]
            row_buttons = []
            for game_cmd, game_text in row_games:
                row_buttons.append({
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {"type": "message", 
                              "label": GAME_LABELS.get(game_cmd, game_cmd), 
                              "text": game_text},
                    "color": c["text2"],
                    "flex": 1
                })
            
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "xs",
                "margin": "sm",
                "contents": row_buttons
            })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "text", "text": "أوامر اللعب: لمح | جاوب | ايقاف", 
             "size": "xxs", "align": "center", "color": c["text3"], "margin": "sm"},
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": [UI._button("رجوع", "بداية", "secondary", c["text2"], c)]
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
            {
                "title": "الأوامر الأساسية",
                "icon": "⚙",
                "items": [
                    "بداية - الصفحة الرئيسية",
                    "تسجيل - إنشاء حساب",
                    "العاب - قائمة الألعاب",
                    "نقاطي - إحصائياتك",
                    "الصدارة - المتصدرين"
                ]
            },
            {
                "title": "أوامر اللعب",
                "icon": "🎮",
                "items": [
                    "لمح - الحصول على تلميح",
                    "جاوب - إظهار الإجابة",
                    "ايقاف - إنهاء اللعبة"
                ]
            },
            {
                "title": "الأوامر التفاعلية",
                "icon": "💬",
                "items": [
                    "سؤال - أسئلة عشوائية",
                    "تحدي - تحديات ممتعة",
                    "اعتراف - اعترافات",
                    "منشن - منشن لأصدقائك",
                    "حكمة - حكم وأقوال",
                    "موقف - مواقف افتراضية"
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
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"{section['icon']} {section['title']}", 
                     "size": "sm", "weight": "bold", "color": c["text"], "margin": "md"}
                ] + [
                    {"type": "text", "text": f"• {item}", 
                     "size": "xs", "color": c["text2"], "margin": "xs", "wrap": True}
                    for item in section["items"]
                ],
                "backgroundColor": c["card"],
                "paddingAll": "12px",
                "cornerRadius": "8px",
                "margin": "md"
            })
        
        contents.extend([
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": [UI._button("رجوع", "بداية", "secondary", c["text2"], c)]
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
        c = UI._c(theme)
        win_rate = int((user['wins'] / user['games'] * 100)) if user['games'] > 0 else 0
        
        stats = [
            {"label": "النقاط", "value": str(user['points']), "highlight": True},
            {"label": "الألعاب", "value": str(user['games'])},
            {"label": "الانتصارات", "value": str(user['wins'])},
            {"label": "نسبة الفوز", "value": f"{win_rate}%"}
        ]
        
        stats_contents = []
        for stat in stats:
            stats_contents.append({
                "type": "box",
                "layout": "horizontal",
                "margin": "sm",
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
            {"type": "text", "text": "إحصائياتك", "size": "xl", 
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "text", "text": user['name'], "size": "md", 
             "align": "center", "color": c["text2"], "margin": "sm"},
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
                "spacing": "sm",
                "contents": [
                    UI._button("رجوع", "بداية", "secondary", c["text2"], c),
                    UI._button("المتصدرين", "الصدارة", "secondary", c["text2"], c)
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
        c = UI._c(theme)
        
        contents = [
            {"type": "text", "text": "المتصدرين", "size": "xl", 
             "weight": "bold", "align": "center", "color": c["primary"]},
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        medals = ["🥇", "🥈", "🥉"]
        for i, leader in enumerate(leaders[:10]):
            rank_display = medals[i] if i < 3 else f"{i + 1}."
            
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "margin": "sm",
                "paddingAll": "8px" if i < 3 else "4px",
                "backgroundColor": c["card"] if i < 3 else "none",
                "cornerRadius": "8px" if i < 3 else "none",
                "contents": [
                    {"type": "text", "text": rank_display, 
                     "size": "md" if i < 3 else "sm",
                     "weight": "bold" if i < 3 else "regular",
                     "color": c["primary"] if i < 3 else c["text3"],
                     "flex": 0},
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
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "md",
                "contents": [UI._button("رجوع", "بداية", "secondary", c["text2"], c)]
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
