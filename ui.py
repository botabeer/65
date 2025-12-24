"""
Bot 65 - UI Module
واجهات المستخدم مع ثيم فاتح وداكن
"""


class UI:
    """بناء واجهات Flex Messages"""
    
    THEMES = {
        'light': {
            'primary': '#2563EB',
            'success': '#10B981',
            'warning': '#F59E0B',
            'error': '#EF4444',
            'text': '#1F2937',
            'text2': '#6B7280',
            'bg': '#FFFFFF',
            'bg2': '#F3F4F6',
            'border': '#E5E7EB'
        },
        'dark': {
            'primary': '#3B82F6',
            'success': '#34D399',
            'warning': '#FBBF24',
            'error': '#F87171',
            'text': '#F9FAFB',
            'text2': '#D1D5DB',
            'bg': '#1F2937',
            'bg2': '#374151',
            'border': '#4B5563'
        }
    }
    
    @staticmethod
    def _c(theme):
        """الحصول على الألوان"""
        return UI.THEMES.get(theme, UI.THEMES['light'])
    
    @staticmethod
    def welcome(name, registered, theme='light'):
        """بطاقة الترحيب"""
        c = UI._c(theme)
        status = "مسجل" if registered else "غير مسجل"
        status_color = c['success'] if registered else c['warning']
        
        return {
            "type": "bubble",
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
                    {"type": "separator", "margin": "lg", "color": c['border']},
                    {
                        "type": "text",
                        "text": f"مرحبا {name}",
                        "size": "lg",
                        "color": c['text'],
                        "align": "center",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": status,
                        "size": "sm",
                        "color": status_color,
                        "align": "center",
                        "margin": "md"
                    },
                    {"type": "separator", "margin": "lg", "color": c['border']},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "العاب", "text": "العاب"},
                                "style": "primary",
                                "color": c['primary'],
                                "height": "sm"
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "نقاطي", "text": "نقاطي"},
                                "style": "primary",
                                "color": c['primary'],
                                "height": "sm"
                            }
                        ],
                        "spacing": "sm",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "الصدارة", "text": "الصدارة"},
                                "style": "secondary",
                                "height": "sm"
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "مساعدة", "text": "مساعدة"},
                                "style": "secondary",
                                "height": "sm"
                            }
                        ],
                        "spacing": "sm",
                        "margin": "sm"
                    },
                    {"type": "separator", "margin": "lg", "color": c['border']},
                    {
                        "type": "text",
                        "text": "للتسجيل: تسجيل [اسمك]",
                        "size": "xs",
                        "color": c['text2'],
                        "align": "center",
                        "margin": "md"
                    }
                ],
                "backgroundColor": c['bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def games_menu(theme='light'):
        """قائمة الألعاب"""
        c = UI._c(theme)
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "قائمة الألعاب",
                        "weight": "bold",
                        "size": "xl",
                        "color": c['primary'],
                        "align": "center"
                    },
                    {"type": "separator", "margin": "lg", "color": c['border']},
                    {
                        "type": "text",
                        "text": "العاب تنافسية",
                        "size": "md",
                        "color": c['text'],
                        "weight": "bold",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "button", "action": {"type": "message", "label": "أغنية", "text": "اغنيه"}, "style": "primary", "color": c['primary'], "height": "sm"},
                            {"type": "button", "action": {"type": "message", "label": "أضداد", "text": "ضد"}, "style": "primary", "color": c['primary'], "height": "sm"}
                        ],
                        "spacing": "sm",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "button", "action": {"type": "message", "label": "سلسلة", "text": "سلسله"}, "style": "primary", "color": c['primary'], "height": "sm"},
                            {"type": "button", "action": {"type": "message", "label": "كتابة", "text": "اسرع"}, "style": "primary", "color": c['primary'], "height": "sm"}
                        ],
                        "spacing": "sm",
                        "margin": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "button", "action": {"type": "message", "label": "تكوين", "text": "تكوين"}, "style": "primary", "color": c['primary'], "height": "sm"},
                            {"type": "button", "action": {"type": "message", "label": "فئة", "text": "فئه"}, "style": "primary", "color": c['primary'], "height": "sm"}
                        ],
                        "spacing": "sm",
                        "margin": "sm"
                    },
                    {"type": "separator", "margin": "lg", "color": c['border']},
                    {
                        "type": "text",
                        "text": "العاب ترفيهية",
                        "size": "md",
                        "color": c['text'],
                        "weight": "bold",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "button", "action": {"type": "message", "label": "لعبة", "text": "لعبه"}, "style": "secondary", "height": "sm"},
                            {"type": "button", "action": {"type": "message", "label": "توافق", "text": "توافق"}, "style": "secondary", "height": "sm"}
                        ],
                        "spacing": "sm",
                        "margin": "md"
                    }
                ],
                "backgroundColor": c['bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def help_card(theme='light'):
        """بطاقة المساعدة"""
        c = UI._c(theme)
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "دليل الاستخدام", "weight": "bold", "size": "xl", "color": c['primary'], "align": "center"},
                    {"type": "separator", "margin": "lg", "color": c['border']},
                    UI._section("الأوامر الأساسية", "بداية - العاب - نقاطي - الصدارة - تسجيل", c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._section("أوامر نصية (بدون تسجيل)", "سؤال - تحدي - اعتراف - منشن - حكمة - موقف", c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._section("الألعاب (تحتاج تسجيل)", "اغنيه - ضد - سلسلة - اسرع - تكوين - فئة - لعبة - توافق", c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._section("أثناء اللعب", "لمح: تلميح | جاوب: الإجابة | انسحب: الخروج والاحتفاظ بالنقاط", c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    UI._section("النقاط", "كل إجابة صحيحة = 1 نقطة | الانسحاب = الاحتفاظ بالنقاط", c),
                    {"type": "separator", "margin": "md", "color": c['border']},
                    {"type": "text", "text": "للتبديل بين الثيم الفاتح والداكن\nاكتب: ثيم", "size": "xs", "color": c['text2'], "align": "center", "wrap": True, "margin": "md"}
                ],
                "backgroundColor": c['bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def stats(user, theme='light'):
        """بطاقة الإحصائيات"""
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
                    UI._stat("النقاط", str(user['points']), c),
                    UI._stat("الألعاب", str(user['games']), c),
                    UI._stat("الفوز", str(user['wins']), c),
                    UI._stat("نسبة الفوز", f"{rate}%", c)
                ],
                "backgroundColor": c['bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def leaderboard(leaders, theme='light'):
        """لوحة الصدارة"""
        c = UI._c(theme)
        contents = [
            {"type": "text", "text": "لوحة الصدارة", "weight": "bold", "size": "xl", "color": c['primary'], "align": "center"},
            {"type": "separator", "margin": "lg", "color": c['border']}
        ]
        
        if not leaders:
            contents.append({"type": "text", "text": "لا توجد بيانات", "size": "sm", "color": c['text2'], "align": "center", "margin": "lg"})
        else:
            for i, leader in enumerate(leaders[:20], 1):
                contents.append(UI._leader(str(i), leader['name'], str(leader['points']), c))
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "backgroundColor": c['bg'],
                "paddingAll": "20px"
            }
        }
    
    @staticmethod
    def _section(title, content, c):
        """قسم معلومات"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": title, "weight": "bold", "size": "sm", "color": c['primary']},
                {"type": "text", "text": content, "size": "xs", "color": c['text2'], "wrap": True, "margin": "xs"}
            ],
            "margin": "md"
        }
    
    @staticmethod
    def _stat(label, value, c):
        """صف إحصائيات"""
        return {
            "type": "box",
            "layout": "baseline",
            "contents": [
                {"type": "text", "text": label, "size": "sm", "color": c['text2'], "flex": 3},
                {"type": "text", "text": value, "size": "lg", "weight": "bold", "color": c['primary'], "align": "end", "flex": 2}
            ],
            "margin": "md"
        }
    
    @staticmethod
    def _leader(rank, name, points, c):
        """صف متصدر"""
        medals = {"1": "1.", "2": "2.", "3": "3."}
        rank_text = medals.get(rank, rank + ".")
        
        return {
            "type": "box",
            "layout": "baseline",
            "contents": [
                {"type": "text", "text": rank_text, "size": "sm", "color": c['text2'], "flex": 0, "weight": "bold" if rank in medals else "regular"},
                {"type": "text", "text": name, "size": "sm", "color": c['text'], "flex": 4, "margin": "sm"},
                {"type": "text", "text": points, "size": "sm", "weight": "bold", "color": c['primary'], "align": "end", "flex": 1}
            ],
            "margin": "sm",
            "paddingAll": "8px",
            "backgroundColor": c['bg2'] if rank in medals else c['bg'],
            "cornerRadius": "8px"
        }
