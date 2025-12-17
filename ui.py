from config import Config
from datetime import datetime, timedelta

class UI:
    @staticmethod
    def main_menu(user, db):
        c = Config.THEMES[user['theme']]
        can_reward = db.can_claim_reward(user['user_id'])
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "Bot Mesh",
                                "size": "xxl",
                                "weight": "bold",
                                "color": c["primary"]
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": c["border"]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"مرحبا {user['name']}",
                                "size": "lg",
                                "color": c["text"]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"النقاط: {user['points']}",
                                        "size": "sm",
                                        "color": c["success"]
                                    },
                                    {
                                        "type": "text",
                                        "text": f"الألعاب: {user['games']}",
                                        "size": "sm",
                                        "color": c["info"],
                                        "align": "end"
                                    }
                                ],
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"الفوز: {user['wins']}",
                                        "size": "sm",
                                        "color": c["warning"]
                                    },
                                    {
                                        "type": "text",
                                        "text": f"السلسلة: {user['streak']}",
                                        "size": "sm",
                                        "color": c["danger"],
                                        "align": "end"
                                    }
                                ],
                                "margin": "sm"
                            }
                        ],
                        "margin": "lg",
                        "paddingAll": "15px",
                        "backgroundColor": c["hover"],
                        "cornerRadius": "8px"
                    }
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "الألعاب", "text": "العاب"},
                                "style": "primary",
                                "color": c["primary"]
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "الصدارة", "text": "الصداره"},
                                "style": "primary",
                                "color": c["secondary"]
                            }
                        ],
                        "spacing": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "إنجازات", "text": "انجازات"},
                                "style": "secondary",
                                "color": c["info"]
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "مكافأة" if can_reward else "تم", "text": "مكافأة"},
                                "style": "secondary",
                                "color": c["success"] if can_reward else c["text_secondary"]
                            }
                        ],
                        "spacing": "sm",
                        "margin": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "تغيير الثيم", "text": "ثيم"},
                                "style": "secondary",
                                "color": c["warning"]
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "مساعدة", "text": "مساعده"},
                                "style": "secondary",
                                "color": c["danger"]
                            }
                        ],
                        "spacing": "sm",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "15px"
            }
        }
        
        return {"type": "flex", "altText": "القائمة الرئيسية", "contents": bubble}
    
    @staticmethod
    def games_list(theme="light"):
        c = Config.THEMES[theme]
        
        games = [
            ["ذكاء", "ألغاز ذكاء"],
            ["خمن", "خمن الكلمة"],
            ["رياضيات", "عمليات حسابية"],
            ["ترتيب", "ترتيب الحروف"],
            ["ضد", "الأضداد"],
            ["كتابه", "كتابة سريعة"],
            ["سلسله", "سلسلة الكلمات"],
            ["انسان", "إنسان حيوان"],
            ["كلمات", "تكوين كلمات"],
            ["اغنيه", "خمن الأغنية"],
            ["الوان", "الألوان"],
            ["توافق", "التوافق"]
        ]
        
        contents = [
            {
                "type": "text",
                "text": "اختر لعبة",
                "size": "xl",
                "weight": "bold",
                "color": c["primary"]
            },
            {
                "type": "separator",
                "margin": "md",
                "color": c["border"]
            }
        ]
        
        for i in range(0, len(games), 2):
            row_buttons = []
            for j in range(2):
                if i + j < len(games):
                    cmd, label = games[i + j]
                    row_buttons.append({
                        "type": "button",
                        "action": {"type": "message", "label": label, "text": cmd},
                        "style": "primary",
                        "color": c["primary"],
                        "height": "sm"
                    })
            
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "contents": row_buttons,
                "spacing": "sm",
                "margin": "md"
            })
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            }
        }
        
        return {"type": "flex", "altText": "قائمة الألعاب", "contents": bubble}
    
    @staticmethod
    def leaderboard(leaders, theme="light"):
        c = Config.THEMES[theme]
        
        contents = [
            {
                "type": "text",
                "text": "لوحة الصدارة",
                "size": "xl",
                "weight": "bold",
                "color": c["primary"]
            },
            {
                "type": "separator",
                "margin": "md",
                "color": c["border"]
            }
        ]
        
        medals = ["🥇", "🥈", "🥉"]
        
        for idx, leader in enumerate(leaders[:10]):
            rank = idx + 1
            medal = medals[idx] if idx < 3 else f"{rank}."
            
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": medal,
                        "size": "lg",
                        "flex": 1
                    },
                    {
                        "type": "text",
                        "text": leader['name'],
                        "size": "md",
                        "color": c["text"],
                        "flex": 4
                    },
                    {
                        "type": "text",
                        "text": str(leader['points']),
                        "size": "sm",
                        "color": c["success"],
                        "align": "end",
                        "flex": 2
                    }
                ],
                "margin": "md",
                "paddingAll": "10px",
                "backgroundColor": c["hover"] if idx < 3 else c["bg"],
                "cornerRadius": "8px"
            })
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            }
        }
        
        return {"type": "flex", "altText": "لوحة الصدارة", "contents": bubble}
    
    @staticmethod
    def achievements_list(user_achievements, theme="light"):
        c = Config.THEMES[theme]
        
        contents = [
            {
                "type": "text",
                "text": "الإنجازات",
                "size": "xl",
                "weight": "bold",
                "color": c["primary"]
            },
            {
                "type": "separator",
                "margin": "md",
                "color": c["border"]
            }
        ]
        
        for achievement_id, achievement in Config.ACHIEVEMENTS.items():
            unlocked = achievement_id in user_achievements
            
            contents.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{'✓' if unlocked else '○'} {achievement['name']}",
                        "size": "md",
                        "weight": "bold",
                        "color": c["success"] if unlocked else c["text_secondary"]
                    },
                    {
                        "type": "text",
                        "text": achievement['desc'],
                        "size": "sm",
                        "color": c["text_secondary"],
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": f"+{achievement['points']} نقطة",
                        "size": "xs",
                        "color": c["warning"]
                    }
                ],
                "margin": "md",
                "paddingAll": "10px",
                "backgroundColor": c["hover"] if unlocked else c["bg"],
                "cornerRadius": "8px"
            })
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            }
        }
        
        return {"type": "flex", "altText": "الإنجازات", "contents": bubble}
    
    @staticmethod
    def achievement_unlocked(achievement, theme="light"):
        c = Config.THEMES[theme]
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "إنجاز جديد",
                        "size": "xl",
                        "weight": "bold",
                        "color": c["success"]
                    },
                    {
                        "type": "text",
                        "text": f"✓ {achievement['name']}",
                        "size": "lg",
                        "weight": "bold",
                        "color": c["text"],
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": achievement['desc'],
                        "size": "md",
                        "color": c["text_secondary"],
                        "wrap": True,
                        "margin": "sm"
                    },
                    {
                        "type": "text",
                        "text": f"حصلت على +{achievement['points']} نقطة",
                        "size": "sm",
                        "color": c["warning"],
                        "margin": "md"
                    }
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            }
        }
        
        return {"type": "flex", "altText": "إنجاز جديد", "contents": bubble}
