import logging
import os
from datetime import datetime
from config import normalize_arabic

def setup_logging():
    """إعداد نظام التسجيل - فقط للأخطاء"""
    
    # إنشاء مجلد logs إذا لم يكن موجوداً
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # إعداد الـ Logger
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)  # فقط الأخطاء
    
    # Handler للملف
    file_handler = logging.FileHandler(
        f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.ERROR)
    
    # Handler للـ Console (في حالة التطوير)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # تنسيق الرسائل
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def format_game_result(game_name, score, total, theme="light"):
    """تنسيق نتيجة اللعبة"""
    from config import THEMES
    
    c = THEMES[theme]
    percentage = (score / total) * 100 if total > 0 else 0
    
    # تحديد الرسالة حسب النتيجة
    if percentage == 100:
        message = "ممتاز! إجابات صحيحة 100%"
        emoji = "🏆"
        color = c["success"]
    elif percentage >= 80:
        message = "رائع! أداء ممتاز"
        emoji = "🌟"
        color = c["success"]
    elif percentage >= 60:
        message = "جيد جداً! واصل التقدم"
        emoji = "👍"
        color = c["info"]
    elif percentage >= 40:
        message = "جيد! يمكنك التحسن"
        emoji = "💪"
        color = c["warning"]
    else:
        message = "حاول مرة أخرى!"
        emoji = "🔄"
        color = c["danger"]
    
    return {
        "type": "flex",
        "altText": f"نتيجة {game_name}",
        "contents": {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{emoji} انتهت اللعبة",
                        "size": "xl",
                        "weight": "bold",
                        "color": color,
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": c["border"]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": game_name,
                                "size": "lg",
                                "color": c["text"],
                                "align": "center",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": f"{score} / {total}",
                                "size": "xxl",
                                "color": color,
                                "align": "center",
                                "weight": "bold",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": f"{percentage:.0f}%",
                                "size": "lg",
                                "color": c["text_secondary"],
                                "align": "center",
                                "margin": "sm"
                            },
                            {
                                "type": "text",
                                "text": message,
                                "size": "md",
                                "color": c["text"],
                                "align": "center",
                                "wrap": True,
                                "margin": "lg"
                            }
                        ],
                        "margin": "lg",
                        "paddingAll": "20px",
                        "backgroundColor": c["hover"],
                        "cornerRadius": "12px"
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
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "العب مرة أخرى",
                            "text": game_name
                        },
                        "style": "primary",
                        "color": c["primary"],
                        "height": "sm"
                    }
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "15px"
            }
        }
    }


def create_progress_bar(current, total, theme="light"):
    """إنشاء شريط تقدم بصري"""
    from config import THEMES
    
    c = THEMES[theme]
    percentage = (current / total) * 100 if total > 0 else 0
    
    # إنشاء مربعات الشريط
    filled = int(percentage / 10)
    empty = 10 - filled
    
    bar = "█" * filled + "░" * empty
    
    return f"{bar} {current}/{total}"


def validate_player_name(name):
    """التحقق من صحة اسم اللاعب"""
    from config import SYSTEM_SETTINGS
    
    if not name or not name.strip():
        return False, "الاسم فارغ"
    
    name = name.strip()
    
    if len(name) < SYSTEM_SETTINGS["min_name_length"]:
        return False, f"الاسم قصير جداً (الحد الأدنى: {SYSTEM_SETTINGS['min_name_length']})"
    
    if len(name) > SYSTEM_SETTINGS["max_name_length"]:
        return False, f"الاسم طويل جداً (الحد الأقصى: {SYSTEM_SETTINGS['max_name_length']})"
    
    return True, name


def parse_command(text):
    """تحليل الأمر من النص"""
    if not text:
        return None, None
    
    text = text.strip()
    normalized = normalize_arabic(text)
    
    # استخراج الأمر والمعاملات
    parts = text.split(maxsplit=1)
    command = normalize_arabic(parts[0])
    args = parts[1] if len(parts) > 1 else None
    
    return command, args


def format_leaderboard(players, theme="light"):
    """تنسيق لوحة الصدارة للقروب"""
    from config import THEMES
    
    c = THEMES[theme]
    
    if not players:
        return {
            "type": "text",
            "text": "لا يوجد لاعبون بعد"
        }
    
    medals = ["🥇", "🥈", "🥉"]
    
    contents = [
        {
            "type": "text",
            "text": "🏆 لوحة الصدارة",
            "size": "xl",
            "weight": "bold",
            "color": c["primary"],
            "align": "center"
        },
        {
            "type": "separator",
            "margin": "md",
            "color": c["border"]
        }
    ]
    
    for idx, player in enumerate(players[:10]):
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
                    "flex": 1,
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": player.display_name,
                    "size": "md",
                    "color": c["text"],
                    "flex": 4
                },
                {
                    "type": "text",
                    "text": str(player.score),
                    "size": "md",
                    "color": c["success"],
                    "align": "end",
                    "weight": "bold",
                    "flex": 2
                }
            ],
            "margin": "md",
            "paddingAll": "10px",
            "backgroundColor": c["hover"] if idx < 3 else c["bg"],
            "cornerRadius": "8px"
        })
    
    return {
        "type": "flex",
        "altText": "لوحة الصدارة",
        "contents": {
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
    }
