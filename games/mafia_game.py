from linebot.models import TextSendMessage, FlexSendMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage
import random
from datetime import datetime, timedelta
from constants import MAFIA_CONFIG, COLORS

class MafiaGame:

    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.players = {}
        self.phase = "registration"
        self.day = 0
        self.votes = {}
        self.night_actions = {}
        self.group_id = None
        self.mafia_target = None
        self.doctor_target = None
        self.detective_check = None

    def start_game(self):
        self.phase = "registration"
        self.players = {}
        self.votes = {}
        self.night_actions = {}
        self.day = 0
        return self.registration_flex()

    def registration_flex(self):
        player_list = []
        for i, (uid, p) in enumerate(self.players.items(), 1):
            player_list.append({
                "type": "text",
                "text": f"{i}. {p['name']}",
                "size": "sm",
                "color": COLORS['text_dark'],
                "margin": "xs" if i > 1 else "md"
            })
        
        if not player_list:
            player_list = [{
                "type": "text",
                "text": "لا يوجد لاعبين بعد",
                "size": "sm",
                "color": COLORS['text_light'],
                "margin": "md",
                "align": "center"
            }]
        
        return FlexSendMessage(
            alt_text="لعبة المافيا",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "لعبة المافيا",
                            "size": "xl",
                            "weight": "bold",
                            "color": COLORS['text_dark'],
                            "align": "center"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "شرح اللعبة", "size": "md", "weight": "bold", "color": COLORS['text_dark']},
                                {"type": "text", "text": "لعبة جماعية تنقسم فيها الأدوار بين المافيا والمواطنين", "size": "xs", "color": COLORS['text_light'], "wrap": True, "margin": "sm"},
                                {"type": "text", "text": "المافيا: يحاولون قتل المواطنين ليلاً", "size": "xs", "color": COLORS['text_light'], "wrap": True, "margin": "xs"},
                                {"type": "text", "text": "الدكتور: يحمي شخص واحد كل ليلة (يمكنه حماية نفسه)", "size": "xs", "color": COLORS['text_light'], "wrap": True, "margin": "xs"},
                                {"type": "text", "text": "المحقق: يتحقق من دور شخص كل ليلة", "size": "xs", "color": COLORS['text_light'], "wrap": True, "margin": "xs"},
                                {"type": "text", "text": "المواطنون: يصوتون لطرد المشتبه بهم نهاراً", "size": "xs", "color": COLORS['text_light'], "wrap": True, "margin": "xs"}
                            ],
                            "backgroundColor": "#F5F5F5",
                            "paddingAll": "15px",
                            "cornerRadius": "10px",
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {"type": "text", "text": f"{len(self.players)}/{MAFIA_CONFIG['min_players']}", "size": "xl", "weight": "bold", "color": "#4CAF50" if len(self.players) >= MAFIA_CONFIG['min_players'] else COLORS['text_dark'], "align": "center"},
                                        {"type": "text", "text": "اللاعبون", "size": "xs", "color": COLORS['text_light'], "align": "center", "margin": "xs"}
                                    ],
                                    "flex": 1
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {"type": "text", "text": str(MAFIA_CONFIG['min_players']), "size": "xl", "weight": "bold", "color": COLORS['text_dark'], "align": "center"},
                                        {"type": "text", "text": "مطلوب", "size": "xs", "color": COLORS['text_light'], "align": "center", "margin": "xs"}
                                    ],
                                    "flex": 1
                                }
                            ],
                            "spacing": "md",
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "المنضمون:", "size": "sm", "weight": "bold", "color": COLORS['text_dark']}
                            ] + player_list,
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "ملاحظة مهمة", "size": "xs", "weight": "bold", "color": "#F44336"},
                                {"type": "text", "text": "يجب إضافة البوت كصديق ليصلك دورك بالخاص", "size": "xs", "color": "#F44336", "wrap": True, "margin": "xs"}
                            ],
                            "backgroundColor": "#FFEBEE",
                            "paddingAll": "12px",
                            "cornerRadius": "8px",
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "انضم للعبة", "text": "انضم مافيا"},
                                    "style": "primary",
                                    "color": "#2196F3",
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "ابدأ اللعبة", "text": "بدء مافيا"},
                                    "style": "primary",
                                    "color": "#4CAF50",
                                    "height": "sm",
                                    "margin": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "إلغاء", "text": "إلغاء مافيا"},
                                    "style": "secondary",
                                    "height": "sm",
                                    "margin": "sm"
                                }
                            ],
                            "margin": "lg"
                        }
                    ],
                    "paddingAll": "20px"
                }
            }
        )

    def add_player(self, user_id, name):
        if self.phase != "registration":
            return {"response": TextSendMessage(text="اللعبة بدأت بالفعل")}
        
        if user_id in self.players:
            return {"response": TextSendMessage(text="أنت مسجل بالفعل")}
        
        self.players[user_id] = {"name": name, "role": None, "alive": True}
        return {"response": self.registration_flex()}

    def assign_roles(self):
        if len(self.players) < MAFIA_CONFIG["min_players"]:
            return {"response": TextSendMessage(text=f"عدد اللاعبين غير كاف. الحد الأدنى {MAFIA_CONFIG['min_players']} لاعبين")}

        roles = ["mafia", "detective", "doctor"]
        remaining = len(self.players) - len(roles)
        roles += ["citizen"] * remaining
        random.shuffle(roles)

        for uid, role in zip(self.players.keys(), roles):
            self.players[uid]["role"] = role
            self.send_role_private(uid, role)

        self.phase = "night"
        self.day = 1
        return {"response": [
            TextSendMessage(text="تم توزيع الأدوار في الخاص لكل لاعب"),
            self.night_flex()
        ]}

    def send_role_private(self, user_id, role):
        role_info = {
            "mafia": {
                "title": "أنت المافيا",
                "desc": "دورك: قتل شخص كل ليلة",
                "instruction": "ستستلم نافذة بأسماء اللاعبين",
                "tip": "اقتل بذكاء واختبئ في النهار",
                "color": "#8B0000"
            },
            "detective": {
                "title": "أنت المحقق",
                "desc": "دورك: فحص شخص كل ليلة",
                "instruction": "ستستلم نافذة بأسماء اللاعبين",
                "tip": "اكتشف المافيا ولمّح في النهار",
                "color": "#1E90FF"
            },
            "doctor": {
                "title": "أنت الدكتور",
                "desc": "دورك: حماية شخص كل ليلة",
                "instruction": "ستستلم نافذة بأسماء اللاعبين",
                "tip": "احمي المهمين وخمّن هدف المافيا",
                "color": "#32CD32"
            },
            "citizen": {
                "title": "أنت مواطن",
                "desc": "دورك: المشاركة في التصويت",
                "instruction": "ليس لك دور في الليل",
                "tip": "راقب وحلل وصوّت بحكمة في النهار",
                "color": "#808080"
            }
        }
        
        info = role_info[role]
        
        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "Bot 65", "weight": "bold", "size": "lg", "color": "#FFFFFF", "align": "center"},
                    {"type": "text", "text": "دورك السري", "size": "md", "color": "#FFFFFF", "align": "center", "margin": "xs"}
                ],
                "backgroundColor": info["color"],
                "paddingAll": "20px",
                "cornerRadius": "10px"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": info["title"], "size": "xxl", "color": COLORS['text_dark'], "weight": "bold", "align": "center"}
                ],
                "margin": "lg"
            },
            {"type": "separator", "margin": "lg", "color": COLORS['border']},
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "دورك", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                    {"type": "text", "text": info["desc"], "size": "sm", "color": COLORS['text_light'], "margin": "md", "wrap": True}
                ],
                "margin": "lg"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "كيف تلعب", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                    {"type": "text", "text": info["instruction"], "size": "sm", "color": COLORS['primary'], "margin": "md", "wrap": True, "weight": "bold"}
                ],
                "margin": "md"
            }
        ]
        
        if role != "citizen":
            contents.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "نصيحة", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                    {"type": "text", "text": info["tip"], "size": "sm", "color": COLORS['text_light'], "margin": "md", "wrap": True}
                ],
                "margin": "md"
            })
            contents.append({"type": "separator", "margin": "lg", "color": COLORS['border']})
            contents.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "انتظر نافذة الليل...", "size": "sm", "color": COLORS['primary'], "align": "center", "weight": "bold"}
                ],
                "margin": "md"
            })
        
        contents.append({"type": "separator", "margin": "lg", "color": COLORS['border']})
        contents.append({
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "لا تشارك دورك مع أحد!", "size": "xs", "color": COLORS['text_light'], "align": "center", "wrap": True}
            ],
            "margin": "md"
        })
        
        flex = FlexSendMessage(
            alt_text="دورك في لعبة المافيا",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": contents,
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        
        try:
            self.line_bot_api.push_message(user_id, flex)
            if role != "citizen":
                import time
                time.sleep(1)
                self.send_action_buttons_private(user_id, role)
        except Exception as e:
            print(f"خطأ في إرسال الدور للاعب {user_id}: {e}")
    
    def send_action_buttons_private(self, user_id, role):
        alive_others = [p for uid, p in self.players.items() if p["alive"] and uid != user_id]
        
        role_configs = {
            "mafia": {
                "title": "اختر من تريد قتله",
                "action": "اقتل",
                "color": "#8B0000",
                "instruction": "اضغط على اسم اللاعب الذي تريد قتله"
            },
            "detective": {
                "title": "اختر من تريد فحصه",
                "action": "افحص",
                "color": "#1E90FF",
                "instruction": "اضغط على اسم اللاعب لمعرفة دوره"
            },
            "doctor": {
                "title": "اختر من تريد حمايته",
                "action": "احمي",
                "color": "#32CD32",
                "instruction": "اضغط على اسم اللاعب لحمايته من المافيا"
            }
        }
        
        config = role_configs.get(role, {})
        action_text = config.get("action", "اختر")
        
        buttons = []
        
        if role == "doctor":
            buttons.append({
                "type": "button",
                "action": {"type": "message", "label": "احمي نفسي", "text": f"{action_text} نفسي"},
                "style": "primary",
                "color": config["color"],
                "height": "sm"
            })
            if alive_others:
                buttons.append({"type": "separator", "margin": "md", "color": COLORS['border']})
        
        for i, p in enumerate(alive_others[:13]):
            buttons.append({
                "type": "button",
                "action": {"type": "message", "label": f"{p['name']}", "text": f"{action_text} {p['name']}"},
                "style": "secondary",
                "height": "sm",
                "margin": "xs" if (i > 0 or role == "doctor") else "none"
            })
        
        flex = FlexSendMessage(
            alt_text=config.get("title", "اختر هدفك"),
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "Bot 65", "weight": "bold", "size": "lg", "color": "#FFFFFF", "align": "center"},
                                {"type": "text", "text": config.get("title", "اختر هدفك"), "size": "md", "color": "#FFFFFF", "align": "center", "margin": "xs", "wrap": True}
                            ],
                            "backgroundColor": config.get("color", COLORS['primary']),
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "التعليمات", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                                {"type": "text", "text": config.get("instruction", "اضغط على اسم اللاعب"), "size": "sm", "color": COLORS['text_light'], "margin": "md", "wrap": True}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": f"اللاعبون الأحياء ({len(alive_others) + 1})", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}
                            ],
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": buttons,
                            "margin": "md"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "اختيارك سري ولن يراه أحد", "size": "xs", "color": COLORS['text_light'], "align": "center", "wrap": True}
                            ],
                            "margin": "md"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
        
        try:
            self.line_bot_api.push_message(user_id, flex)
        except Exception as e:
            print(f"خطأ في إرسال الأزرار للاعب {user_id}: {e}")

    def night_flex(self):
        alive_players = [p for p in self.players.values() if p["alive"]]
        return FlexSendMessage(
            alt_text="مرحلة الليل",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "Bot 65", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": f"اليوم {self.day} - الليل", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "الليل حل", "size": "xl", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                                {"type": "text", "text": "الأدوار الخاصة تعمل الآن", "size": "sm", "color": COLORS['text_light'], "margin": "md", "align": "center"},
                                {"type": "separator", "margin": "md", "color": COLORS['border']},
                                {"type": "text", "text": "تحقق من رسائلك الخاصة", "size": "sm", "color": COLORS['primary'], "margin": "md", "align": "center", "wrap": True},
                                {"type": "text", "text": "استخدم الأزرار للاختيار", "size": "sm", "color": COLORS['primary'], "margin": "xs", "align": "center", "wrap": True},
                                {"type": "separator", "margin": "md", "color": COLORS['border']},
                                {"type": "text", "text": f"اللاعبون الأحياء: {len(alive_players)}", "size": "sm", "color": COLORS['text_light'], "margin": "md", "align": "center"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "حالة اللعبة", "text": "حالة مافيا"},
                                    "style": "secondary",
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "إنهاء الليل", "text": "إنهاء الليل"},
                                    "style": "primary",
                                    "color": COLORS['primary'],
                                    "height": "sm",
                                    "margin": "sm"
                                }
                            ],
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )
    
    def process_night(self):
        messages = []
        
        mafia_target = self.night_actions.get("mafia_target")
        doctor_target = self.night_actions.get("doctor_target")
        
        if mafia_target:
            if mafia_target == doctor_target:
                messages.append("طلع النهار... لم يُقتل أحد الليلة!")
            else:
                self.players[mafia_target]["alive"] = False
                victim_name = self.players[mafia_target]["name"]
                messages.append(f"طلع النهار... تم قتل {victim_name}")
        else:
            messages.append("طلع النهار... لم يُقتل أحد الليلة!")
        
        self.night_actions = {}
        self.phase = "day"
        
        winner_check = self.check_winner()
        if winner_check:
            return winner_check
        
        return {
            "response": [
                TextSendMessage(text=msg) for msg in messages
            ] + [self.day_flex()]
        }

    def day_flex(self):
        alive_players = [p for p in self.players.values() if p["alive"]]
        return FlexSendMessage(
            alt_text="مرحلة النهار",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "Bot 65", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": f"اليوم {self.day} - مرحلة النهار", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "مناقشة ثم التصويت", "size": "lg", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                                {"type": "text", "text": f"اللاعبون الأحياء: {len(alive_players)}", "size": "sm", "color": COLORS['text_light'], "margin": "md", "align": "center"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "تصويت", "text": "تصويت مافيا"},
                                    "style": "primary",
                                    "color": COLORS['primary'],
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {"type": "message", "label": "حالة اللعبة", "text": "حالة مافيا"},
                                    "style": "secondary",
                                    "height": "sm",
                                    "margin": "sm"
                                }
                            ],
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def status_flex(self):
        alive = [p for p in self.players.values() if p["alive"]]
        dead = [p for p in self.players.values() if not p["alive"]]
        
        alive_list = []
        for i, p in enumerate(alive, 1):
            alive_list.append({
                "type": "text",
                "text": f"{i}. {p['name']}",
                "size": "sm",
                "color": COLORS['text_dark'],
                "margin": "xs" if i > 1 else "md"
            })
        
        if not alive_list:
            alive_list = [{"type": "text", "text": "لا يوجد", "size": "sm", "color": COLORS['text_light'], "margin": "md"}]
        
        dead_list = []
        for i, p in enumerate(dead, 1):
            dead_list.append({
                "type": "text",
                "text": f"{i}. {p['name']}",
                "size": "sm",
                "color": COLORS['text_light'],
                "margin": "xs" if i > 1 else "md"
            })
        
        if not dead_list:
            dead_list = [{"type": "text", "text": "لا يوجد", "size": "sm", "color": COLORS['text_light'], "margin": "md"}]
        
        phase_text = {
            "registration": "التسجيل",
            "night": "الليل",
            "day": "النهار",
            "voting": "التصويت",
            "ended": "انتهت"
        }
        
        return FlexSendMessage(
            alt_text="حالة لعبة المافيا",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "Bot 65", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": "حالة لعبة المافيا", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": f"اليوم: {self.day}", "size": "md", "color": COLORS['text_dark'], "weight": "bold"},
                                {"type": "text", "text": f"المرحلة: {phase_text.get(self.phase, self.phase)}", "size": "sm", "color": COLORS['text_light'], "margin": "xs"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "اللاعبون الأحياء", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}
                            ] + alive_list,
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "اللاعبون المقتولون", "size": "md", "color": COLORS['text_dark'], "weight": "bold"}
                            ] + dead_list,
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def voting_flex(self):
        alive = [p for p in self.players.values() if p["alive"]]
        
        buttons = []
        for i, p in enumerate(alive[:10]):
            buttons.append({
                "type": "button",
                "action": {"type": "message", "label": p["name"], "text": f"صوت {p['name']}"},
                "style": "secondary",
                "height": "sm",
                "margin": "xs" if i > 0 else "none"
            })
        
        buttons.append({"type": "separator", "margin": "md"})
        buttons.append({
            "type": "button",
            "action": {"type": "message", "label": "إنهاء التصويت", "text": "إنهاء التصويت"},
            "style": "primary",
            "color": COLORS['primary'],
            "height": "sm",
            "margin": "md"
        })
        
        return FlexSendMessage(
            alt_text="التصويت",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "Bot 65", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": "التصويت", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "اضغط على اسم من تظنه المافيا", "size": "md", "color": COLORS['text_dark'], "weight": "bold", "align": "center", "wrap": True}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": buttons,
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def vote(self, user_id, target_name):
        if self.phase != "voting":
            return {"response": TextSendMessage(text="ليس وقت التصويت")}
        
        if user_id not in self.players or not self.players[user_id]["alive"]:
            return {"response": TextSendMessage(text="لا يمكنك التصويت")}
        
        for uid, p in self.players.items():
            if p["name"] == target_name and p["alive"]:
                self.votes[user_id] = uid
                return {"response": TextSendMessage(text=f"تم تصويتك لـ {target_name}")}
        
        return {"response": TextSendMessage(text="لا يوجد لاعب بهذا الاسم")}

    def end_voting(self):
        if not self.votes:
            self.phase = "night"
            self.day += 1
            return {"response": [
                TextSendMessage(text="لم يتم التصويت. الانتقال لليل"),
                self.night_flex()
            ]}
        
        vote_counts = {}
        for target_uid in self.votes.values():
            vote_counts[target_uid] = vote_counts.get(target_uid, 0) + 1
        
        killed_uid = max(vote_counts, key=vote_counts.get)
        self.players[killed_uid]["alive"] = False
        killed_name = self.players[killed_uid]["name"]
        
        self.votes = {}
        self.phase = "night"
        self.day += 1
        
        result = self.check_winner()
        if result:
            return result
        
        return {"response": [
            TextSendMessage(text=f"تم التصويت على {killed_name} وإعدامه"),
            self.night_flex()
        ]}

    def check_winner(self):
        mafia_count = sum(1 for p in self.players.values() if p["alive"] and p["role"] == "mafia")
        citizen_count = sum(1 for p in self.players.values() if p["alive"] and p["role"] != "mafia")
        
        if mafia_count == 0:
            self.phase = "ended"
            return {"response": self.winner_flex("المواطنون"), "game_over": True}
        
        if mafia_count >= citizen_count:
            self.phase = "ended"
            return {"response": self.winner_flex("المافيا"), "game_over": True}
        
        return None

    def winner_flex(self, winner_team):
        return FlexSendMessage(
            alt_text="نهاية لعبة المافيا",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "Bot 65", "weight": "bold", "size": "lg", "color": COLORS['white'], "align": "center"},
                                {"type": "text", "text": "انتهت اللعبة", "size": "md", "color": COLORS['white'], "align": "center", "margin": "xs"}
                            ],
                            "backgroundColor": COLORS['primary'],
                            "paddingAll": "20px",
                            "cornerRadius": "10px"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "الفائز", "size": "sm", "color": COLORS['text_light'], "align": "center"},
                                {"type": "text", "text": winner_team, "size": "xxl", "color": COLORS['primary'], "weight": "bold", "align": "center", "margin": "md"}
                            ],
                            "margin": "lg"
                        },
                        {"type": "separator", "margin": "lg", "color": COLORS['border']},
                        {
                            "type": "button",
                            "action": {"type": "message", "label": "إعادة", "text": "مافيا"},
                            "style": "primary",
                            "color": COLORS['primary'],
                            "height": "sm",
                            "margin": "lg"
                        }
                    ],
                    "backgroundColor": COLORS['card_bg'],
                    "paddingAll": "20px"
                }
            }
        )

    def check_answer(self, text, user_id, display_name):
        text = text.strip()
        
        if text == "انضم مافيا":
            return self.add_player(user_id, display_name)
        
        if text == "بدء مافيا":
            return self.assign_roles()
        
        if text == "حالة مافيا":
            return {"response": self.status_flex()}
        
        if text == "إلغاء مافيا":
            if self.phase == "registration":
                self.start_game()
                return {"response": TextSendMessage(text="تم إلغاء اللعبة")}
            return {"response": TextSendMessage(text="لا يمكن الإلغاء بعد البدء")}
        
        if text == "إنهاء الليل":
            if self.phase == "night":
                return self.process_night()
            return {"response": TextSendMessage(text="ليس وقت الليل الآن")}
        
        if text == "تصويت مافيا":
            if self.phase in ["day", "voting"]:
                self.phase = "voting"
                return {"response": self.voting_flex()}
            return {"response": TextSendMessage(text="ليس وقت التصويت الآن")}
        
        if text.startswith("صوت "):
            target_name = text.replace("صوت ", "").strip()
            return self.vote(user_id, target_name)
        
        if text == "إنهاء التصويت":
            if self.phase == "voting":
                return self.end_voting()
            return {"response": TextSendMessage(text="ليس وقت التصويت")}
        
        if text.startswith("اقتل "):
            if user_id not in self.players or self.players[user_id]["role"] != "mafia":
                return {"response": TextSendMessage(text="أنت لست المافيا")}
            if self.phase != "night":
                return {"response": TextSendMessage(text="ليس وقت الليل")}
            
            target_name = text.replace("اقتل ", "").strip()
            for uid, p in self.players.items():
                if p["name"] == target_name and p["alive"] and uid != user_id:
                    self.night_actions["mafia_target"] = uid
                    
                    confirm_flex = FlexSendMessage(
                        alt_text="تأكيد الاختيار",
                        contents={
                            "type": "bubble",
                            "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {"type": "text", "text": "تم الاختيار", "weight": "bold", "size": "xl", "color": "#FFFFFF", "align": "center"}
                                        ],
                                        "backgroundColor": "#8B0000",
                                        "paddingAll": "20px",
                                        "cornerRadius": "10px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {"type": "text", "text": "الضحية", "size": "md", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                                            {"type": "text", "text": target_name, "size": "xxl", "color": "#8B0000", "weight": "bold", "align": "center", "margin": "md"}
                                        ],
                                        "margin": "lg"
                                    },
                                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {"type": "text", "text": "سيتم قتله عند إنهاء الليل", "size": "sm", "color": COLORS['text_light'], "align": "center", "wrap": True}
                                        ],
                                        "margin": "md"
                                    }
                                ],
                                "backgroundColor": COLORS['card_bg'],
                                "paddingAll": "20px"
                            }
                        }
                    )
                    return {"response": confirm_flex}
            return {"response": TextSendMessage(text="لا يوجد لاعب بهذا الاسم")}
        
        if text.startswith("افحص "):
            if user_id not in self.players or self.players[user_id]["role"] != "detective":
                return {"response": TextSendMessage(text="أنت لست المحقق")}
            if self.phase != "night":
                return {"response": TextSendMessage(text="ليس وقت الليل")}
            
            target_name = text.replace("افحص ", "").strip()
            for uid, p in self.players.items():
                if p["name"] == target_name and p["alive"] and uid != user_id:
                    role = p["role"]
                    
                    if role == "mafia":
                        result_color = "#8B0000"
                        result_text = "مافيا!"
                        result_desc = "هذا اللاعب هو المافيا"
                    else:
                        result_color = "#32CD32"
                        result_text = "بريء"
                        result_desc = "هذا اللاعب ليس المافيا"
                    
                    result_flex = FlexSendMessage(
                        alt_text="نتيجة الفحص",
                        contents={
                            "type": "bubble",
                            "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {"type": "text", "text": "نتيجة الفحص", "weight": "bold", "size": "xl", "color": "#FFFFFF", "align": "center"}
                                        ],
                                        "backgroundColor": "#1E90FF",
                                        "paddingAll": "20px",
                                        "cornerRadius": "10px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {"type": "text", "text": target_name, "size": "xl", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                                            {"type": "text", "text": result_text, "size": "xxl", "color": result_color, "weight": "bold", "align": "center", "margin": "md"}
                                        ],
                                        "margin": "lg"
                                    },
                                    {"type": "separator", "margin": "lg", "color": COLORS['border']},
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {"type": "text", "text": result_desc, "size": "sm", "color": COLORS['text_light'], "align": "center", "wrap": True}
                                        ],
                                        "margin": "md"
                                    }
                                ],
                                "backgroundColor": COLORS['card_bg'],
                                "paddingAll": "20px"
                            }
                        }
                    )
                    return {"response": result_flex}
            return {"response": TextSendMessage(text="لا يوجد لاعب بهذا الاسم")}
        
        if text.startswith("احمي "):
            if user_id not in self.players or self.players[user_id]["role"] != "doctor":
                return {"response": TextSendMessage(text="أنت لست الدكتور")}
            if self.phase != "night":
                return {"response": TextSendMessage(text="ليس وقت الليل")}
            
            target_text = text.replace("احمي ", "").strip()
            
            if target_text == "نفسي":
                self.night_actions["doctor_target"] = user_id
                target_display = "نفسك"
            else:
                found = False
                for uid, p in self.players.items():
                    if p["name"] == target_text and p["alive"]:
                        self.night_actions["doctor_target"] = uid
                        target_display = target_text
                        found = True
                        break
                
                if not found:
                    return {"response": TextSendMessage(text="لا يوجد لاعب بهذا الاسم")}
            
            confirm_flex = FlexSendMessage(
                alt_text="تأكيد الحماية",
                contents={
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {"type": "text", "text": "تم الاختيار", "weight": "bold", "size": "xl", "color": "#FFFFFF", "align": "center"}
                                ],
                                "backgroundColor": "#32CD32",
                                "paddingAll": "20px",
                                "cornerRadius": "10px"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {"type": "text", "text": "المحمي", "size": "md", "color": COLORS['text_dark'], "weight": "bold", "align": "center"},
                                    {"type": "text", "text": target_display, "size": "xxl", "color": "#32CD32", "weight": "bold", "align": "center", "margin": "md"}
                                ],
                                "margin": "lg"
                            },
                            {"type": "separator", "margin": "lg", "color": COLORS['border']},
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {"type": "text", "text": "سيتم حمايته من المافيا الليلة", "size": "sm", "color": COLORS['text_light'], "align": "center", "wrap": True}
                                ],
                                "margin": "md"
                            }
                        ],
                        "backgroundColor": COLORS['card_bg'],
                        "paddingAll": "20px"
                    }
                }
            )
            return {"response": confirm_flex}
        
        return None
