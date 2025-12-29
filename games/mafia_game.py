from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer, PushMessageRequest
import random
from games.base_game import BaseGame
import logging

logger = logging.getLogger(__name__)

class MafiaGame(BaseGame):
    """لعبة المافيا - لعبة جماعية احترافية"""
    
    def __init__(self, line_bot_api, theme='light'):
        super().__init__(line_bot_api, theme=theme)
        self.game_name = "مافيا"
        self.supports_hint = False
        self.supports_reveal = False
        
        self.players = {}
        self.phase = "registration"
        self.day_number = 0
        self.night_actions = {'mafia_target': None, 'doctor_target': None, 'detective_check': None}
        self.votes = {}
        self.min_players = 4
        self.max_players = 15
        self.game_active = False

    def get_question(self):
        """تنفيذ الدالة المطلوبة من BaseGame"""
        return self.registration_message()

    def registration_message(self):
        """شاشة التسجيل الرئيسية"""
        c = self.get_theme_colors()
        player_list = []
        
        for i, (uid, p) in enumerate(self.players.items(), 1):
            player_list.append({
                "type": "text",
                "text": f"{i}. {p['name']}",
                "size": "sm",
                "color": c["text"],
                "margin": "xs" if i > 1 else "md"
            })

        if not player_list:
            player_list = [{
                "type": "text",
                "text": "لا يوجد لاعبين بعد",
                "size": "sm",
                "color": c["text2"],
                "align": "center",
                "margin": "md"
            }]

        current_count = len(self.players)
        ready_text = f"{current_count}/{self.max_players}"
        min_text = f"الحد الادنى: {self.min_players}"

        contents = [
            {
                "type": "text",
                "text": "لعبة المافيا",
                "size": "xl",
                "weight": "bold",
                "color": c["text"],
                "align": "center"
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
                "cornerRadius": "8px",
                "paddingAll": "12px",
                "contents": [
                    {
                        "type": "text",
                        "text": "شرح اللعبة",
                        "size": "md",
                        "weight": "bold",
                        "color": c["text"]
                    },
                    {
                        "type": "text",
                        "text": "لعبة جماعية تنقسم فيها الادوار بين المافيا والمواطنين",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "sm"
                    },
                    {
                        "type": "text",
                        "text": "المافيا: يحاولون قتل المواطنين ليلا",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": "الدكتور: يحمي شخص واحد كل ليلة",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": "المحقق: يتحقق من دور شخص كل ليلة",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": "المواطنون: يصوتون لطرد المشتبه بهم نهارا",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "xs"
                    }
                ]
            },
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "lg",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "flex": 1,
                        "contents": [
                            {
                                "type": "text",
                                "text": str(current_count),
                                "size": "xxl",
                                "weight": "bold",
                                "color": c["text"],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "اللاعبون",
                                "size": "xs",
                                "color": c["text2"],
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
                                "text": str(self.min_players),
                                "size": "xxl",
                                "weight": "bold",
                                "color": c["text"],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "الحد الادنى",
                                "size": "xs",
                                "color": c["text2"],
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
                "layout": "vertical",
                "margin": "lg",
                "contents": [
                    {
                        "type": "text",
                        "text": "الاعبون المسجلون:",
                        "size": "sm",
                        "weight": "bold",
                        "color": c["text"]
                    }
                ] + player_list
            },
            {
                "type": "separator",
                "margin": "lg",
                "color": c["border"]
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "backgroundColor": c["card"],
                "cornerRadius": "8px",
                "paddingAll": "10px",
                "contents": [
                    {
                        "type": "text",
                        "text": "ملاحظة مهمة",
                        "size": "sm",
                        "weight": "bold",
                        "color": c["text"],
                        "margin": "none"
                    },
                    {
                        "type": "text",
                        "text": "يجب اضافة البوت كصديق ليصلك دورك بالخاص",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "xs"
                    }
                ]
            }
        ]

        footer = {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "انضم للعبة",
                        "text": "انضم مافيا"
                    },
                    "style": "primary",
                    "color": "#F8FBFC",
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "ابدأ اللعبة",
                        "text": "بدء مافيا"
                    },
                    "style": "primary",
                    "color": "#F8FBFC",
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "الغاء",
                        "text": "الغاء مافيا"
                    },
                    "style": "secondary",
                    "color": "#F8FBFC",
                    "height": "sm"
                }
            ]
        }

        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": footer
        }
        
        return FlexMessage(alt_text="لعبة المافيا", contents=FlexContainer.from_dict(bubble))

    def add_player(self, user_id, name):
        """اضافة لاعب جديد"""
        if self.phase != "registration":
            return {"response": self.simple_message("اللعبة بدأت بالفعل")}
        
        if user_id in self.players:
            return {"response": self.simple_message("انت مسجل بالفعل")}
        
        if len(self.players) >= self.max_players:
            return {"response": self.simple_message(f"وصل العدد للحد الاقصى ({self.max_players} لاعب)")}
        
        self.players[user_id] = {'name': name, 'role': None, 'alive': True}
        return {"response": self.registration_message()}

    def assign_roles(self):
        """توزيع الادوار على اللاعبين"""
        if len(self.players) < self.min_players:
            return {"response": self.simple_message(f"عدد اللاعبين غير كاف\nالحد الادنى: {self.min_players} لاعبين")}
        
        player_ids = list(self.players.keys())
        random.shuffle(player_ids)
        
        # حساب عدد المافيا (1 مافيا لكل 4 لاعبين)
        num_mafia = max(1, len(player_ids) // 4)
        
        # توزيع الادوار: مافيا + محقق + دكتور + مواطنين
        roles = ['mafia'] * num_mafia + ['detective', 'doctor'] + ['citizen'] * (len(player_ids) - num_mafia - 2)
        
        for uid, role in zip(player_ids, roles):
            self.players[uid]['role'] = role
            self.send_role_private(uid, role)
        
        self.phase = "night"
        self.day_number = 1
        self.game_active = True
        
        return {"response": [
            self.simple_message("تم توزيع الادوار في الخاص\nتحقق من رسائلك الخاصة"),
            self.night_message()
        ]}

    def send_role_private(self, user_id, role):
        """ارسال الدور للاعب في الخاص"""
        role_names = {
            'mafia': 'المافيا',
            'detective': 'المحقق',
            'doctor': 'الدكتور',
            'citizen': 'مواطن'
        }
        
        role_desc = {
            'mafia': 'اقتل شخص من الاحياء كل ليلة',
            'detective': 'افحص شخص من الاحياء كل ليلة',
            'doctor': 'احمي شخص من الاحياء كل ليلة',
            'citizen': 'صوت نهارا لطرد المشتبه بهم'
        }
        
        try:
            c = self.get_theme_colors()
            
            footer_buttons = []
            if role == 'mafia':
                footer_buttons.append({
                    "type": "button",
                    "action": {"type": "message", "label": "اختر الهدف", "text": "اقتل"},
                    "style": "primary",
                    "color": "#F8FBFC",
                    "height": "sm"
                })
            elif role == 'detective':
                footer_buttons.append({
                    "type": "button",
                    "action": {"type": "message", "label": "اختر من تريد فحصه", "text": "افحص"},
                    "style": "primary",
                    "color": "#F8FBFC",
                    "height": "sm"
                })
            elif role == 'doctor':
                footer_buttons.append({
                    "type": "button",
                    "action": {"type": "message", "label": "اختر من تريد حمايته", "text": "احمي"},
                    "style": "primary",
                    "color": "#F8FBFC",
                    "height": "sm"
                })
            
            bubble = {
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": c["bg"],
                    "paddingAll": "20px",
                    "contents": [
                        {
                            "type": "text",
                            "text": "دورك في اللعبة",
                            "size": "xl",
                            "weight": "bold",
                            "color": c["text"],
                            "align": "center"
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
                            "cornerRadius": "8px",
                            "paddingAll": "15px",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": role_names[role],
                                    "size": "lg",
                                    "weight": "bold",
                                    "color": c["text"],
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": role_desc[role],
                                    "size": "sm",
                                    "color": c["text2"],
                                    "wrap": True,
                                    "margin": "md",
                                    "align": "center"
                                }
                            ]
                        }
                    ]
                }
            }
            
            if footer_buttons:
                bubble["footer"] = {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": footer_buttons
                }
            
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[FlexMessage(alt_text="دورك في اللعبة", contents=FlexContainer.from_dict(bubble))]
                )
            )
        except Exception as e:
            logger.error(f"Failed to send role to {user_id}: {e}")

    def night_message(self):
        """رسالة مرحلة الليل"""
        c = self.get_theme_colors()
        alive = [p for p in self.players.values() if p['alive']]
        
        alive_list = []
        for i, p in enumerate(alive, 1):
            alive_list.append({
                "type": "text",
                "text": f"{i}. {p['name']}",
                "size": "sm",
                "color": c["text"],
                "margin": "xs" if i > 1 else "md"
            })
        
        contents = [
            {
                "type": "text",
                "text": f"الليل - اليوم {self.day_number}",
                "size": "xl",
                "weight": "bold",
                "color": c["text"],
                "align": "center"
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
                "cornerRadius": "8px",
                "paddingAll": "12px",
                "contents": [
                    {
                        "type": "text",
                        "text": "المافيا والمحقق والدكتور يعملون الان",
                        "size": "sm",
                        "color": c["text2"],
                        "align": "center",
                        "wrap": True
                    }
                ]
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "contents": [
                    {
                        "type": "text",
                        "text": "الاحياء:",
                        "size": "sm",
                        "weight": "bold",
                        "color": c["text"]
                    }
                ] + alive_list
            },
            {
                "type": "separator",
                "margin": "lg",
                "color": c["border"]
            }
        ]
        
        footer = {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "action": {"type": "message", "label": "انهاء الليل", "text": "انهاء الليل"},
                    "style": "primary",
                    "color": "#F8FBFC",
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {"type": "message", "label": "حالة اللعبة", "text": "حالة مافيا"},
                    "style": "secondary",
                    "color": "#F8FBFC",
                    "height": "sm"
                }
            ]
        }
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": footer
        }
        
        return FlexMessage(alt_text="مافيا - الليل", contents=FlexContainer.from_dict(bubble))

    def process_night(self):
        """معالجة احداث الليل"""
        victim_id = self.night_actions['mafia_target']
        saved_id = self.night_actions['doctor_target']
        
        result_parts = [f"انتهى الليل {self.day_number}"]
        
        if victim_id and victim_id != saved_id:
            self.players[victim_id]['alive'] = False
            result_parts.append(f"تم قتل: {self.players[victim_id]['name']}")
        elif victim_id and victim_id == saved_id:
            result_parts.append("الدكتور انقذ الضحية")
        else:
            result_parts.append("لم يحدث قتل الليلة")
        
        self.night_actions = {'mafia_target': None, 'doctor_target': None, 'detective_check': None}
        
        winner = self.check_winner()
        if winner:
            return {
                "response": [
                    self.simple_message("\n".join(result_parts)),
                    self.winner_message(winner)
                ],
                "game_over": True
            }
        
        self.phase = "night"
        self.day_number += 1
        return {
            "response": [
                self.simple_message("\n".join(result_parts)),
                self.night_message()
            ]
        }

    def check_winner(self):
        """فحص الفائز"""
        alive = [p for p in self.players.values() if p['alive']]
        mafia_count = sum(1 for p in alive if p['role'] == 'mafia')
        citizen_count = len(alive) - mafia_count
        
        if mafia_count == 0:
            return "المواطنون"
        if mafia_count >= citizen_count:
            return "المافيا"
        return None

    def winner_message(self, winner_team):
        """رسالة نهاية اللعبة"""
        c = self.get_theme_colors()
        
        mafia_list = []
        detective_list = []
        doctor_list = []
        citizen_list = []
        
        for p in self.players.values():
            player_text = f"{p['name']}"
            if p['role'] == 'mafia':
                mafia_list.append({
                    "type": "text",
                    "text": player_text,
                    "size": "sm",
                    "color": c["text"],
                    "margin": "xs"
                })
            elif p['role'] == 'detective':
                detective_list.append({
                    "type": "text",
                    "text": player_text,
                    "size": "sm",
                    "color": c["text"],
                    "margin": "xs"
                })
            elif p['role'] == 'doctor':
                doctor_list.append({
                    "type": "text",
                    "text": player_text,
                    "size": "sm",
                    "color": c["text"],
                    "margin": "xs"
                })
            else:
                citizen_list.append({
                    "type": "text",
                    "text": player_text,
                    "size": "sm",
                    "color": c["text"],
                    "margin": "xs"
                })
        
        role_sections = []
        
        if mafia_list:
            role_sections.append({
                "type": "text",
                "text": "المافيا:",
                "size": "sm",
                "weight": "bold",
                "color": c["text"],
                "margin": "lg"
            })
            role_sections.extend(mafia_list)
        
        if detective_list:
            role_sections.append({
                "type": "text",
                "text": "المحقق:",
                "size": "sm",
                "weight": "bold",
                "color": c["text"],
                "margin": "md"
            })
            role_sections.extend(detective_list)
        
        if doctor_list:
            role_sections.append({
                "type": "text",
                "text": "الدكتور:",
                "size": "sm",
                "weight": "bold",
                "color": c["text"],
                "margin": "md"
            })
            role_sections.extend(doctor_list)
        
        if citizen_list:
            role_sections.append({
                "type": "text",
                "text": "المواطنون:",
                "size": "sm",
                "weight": "bold",
                "color": c["text"],
                "margin": "md"
            })
            role_sections.extend(citizen_list)
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "انتهت اللعبة",
                        "size": "xl",
                        "weight": "bold",
                        "color": c["text"],
                        "align": "center"
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
                        "cornerRadius": "8px",
                        "paddingAll": "15px",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الفريق الفائز",
                                "size": "sm",
                                "color": c["text2"],
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": winner_team,
                                "size": "xxl",
                                "weight": "bold",
                                "color": c["text"],
                                "align": "center",
                                "margin": "sm"
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": c["border"]
                    },
                    {
                        "type": "text",
                        "text": "الادوار:",
                        "size": "md",
                        "weight": "bold",
                        "color": c["text"],
                        "margin": "lg"
                    }
                ] + role_sections
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "لعبة جديدة",
                            "text": "مافيا"
                        },
                        "style": "primary",
                        "color": "#F8FBFC",
                        "height": "sm"
                    }
                ]
            }
        }
        
        return FlexMessage(alt_text="نهاية اللعبة", contents=FlexContainer.from_dict(bubble))
    
    def status_message(self):
        """رسالة حالة اللعبة"""
        c = self.get_theme_colors()
        alive = [p for p in self.players.values() if p['alive']]
        dead = [p for p in self.players.values() if not p['alive']]
        
        alive_list = []
        for i, p in enumerate(alive, 1):
            alive_list.append({
                "type": "text",
                "text": f"{i}. {p['name']}",
                "size": "sm",
                "color": c["text"],
                "margin": "xs" if i > 1 else "md"
            })
        
        dead_list = []
        for i, p in enumerate(dead, 1):
            dead_list.append({
                "type": "text",
                "text": f"{i}. {p['name']}",
                "size": "sm",
                "color": c["text2"],
                "margin": "xs" if i > 1 else "md"
            })
        
        if not alive_list:
            alive_list = [{
                "type": "text",
                "text": "لا يوجد",
                "size": "sm",
                "color": c["text2"],
                "margin": "md"
            }]
        
        if not dead_list:
            dead_list = [{
                "type": "text",
                "text": "لا يوجد",
                "size": "sm",
                "color": c["text2"],
                "margin": "md"
            }]
        
        phase_names = {
            'registration': 'التسجيل',
            'night': 'الليل',
            'day': 'النهار',
            'voting': 'التصويت',
            'ended': 'انتهت'
        }
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "حالة اللعبة",
                        "size": "xl",
                        "weight": "bold",
                        "color": c["text"],
                        "align": "center"
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
                        "cornerRadius": "8px",
                        "paddingAll": "12px",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"اليوم: {self.day_number}",
                                "size": "md",
                                "weight": "bold",
                                "color": c["text"]
                            },
                            {
                                "type": "text",
                                "text": f"المرحلة: {phase_names.get(self.phase, self.phase)}",
                                "size": "sm",
                                "color": c["text2"],
                                "margin": "xs"
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
                        "layout": "vertical",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "text",
                                "text": "الاحياء:",
                                "size": "md",
                                "weight": "bold",
                                "color": c["text"]
                            }
                        ] + alive_list
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": c["border"]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "text",
                                "text": "المقتولون:",
                                "size": "md",
                                "weight": "bold",
                                "color": c["text"]
                            }
                        ] + dead_list
                    }
                ]
            }
        }
        
        return FlexMessage(alt_text="حالة اللعبة", contents=FlexContainer.from_dict(bubble))
    
    def simple_message(self, text):
        """انشاء رسالة فلكس بسيطة"""
        c = self.get_theme_colors()
        
        bubble = {
            "type": "bubble",
            "size": "micro",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "15px",
                "contents": [
                    {
                        "type": "text",
                        "text": text,
                        "size": "sm",
                        "color": c["text"],
                        "wrap": True,
                        "align": "center"
                    }
                ]
            }
        }
        
        return FlexMessage(alt_text=text, contents=FlexContainer.from_dict(bubble))
    
    def check_answer(self, text, user_id, display_name):
        """معالجة رسائل اللاعبين"""
        text = text.strip()
        
        # اوامر التسجيل والبداية
        if text == "انضم مافيا":
            return self.add_player(user_id, display_name)
        
        if text == "بدء مافيا":
            return self.assign_roles()
        
        if text == "حالة مافيا":
            return {"response": self.status_message()}
        
        if text == "الغاء مافيا":
            if self.phase == "registration":
                self.game_active = False
                return {
                    "response": self.simple_message("تم الغاء اللعبة"),
                    "game_over": True
                }
            return {"response": self.simple_message("لا يمكن الالغاء بعد بدء اللعبة")}
        
        # اوامر الليل
        if text == "انهاء الليل":
            if self.phase == "night":
                return self.process_night()
            return {"response": self.simple_message("ليس وقت الليل الآن")}
        
        # اوامر النهار والتصويت
        if text == "تصويت مافيا":
            if self.phase in ["day", "voting"]:
                self.phase = "voting"
                return {"response": self.voting_message()}
            return {"response": self.simple_message("ليس وقت التصويت الآن")}
        
        if text.startswith("صوت "):
            target_name = text.replace("صوت ", "").strip()
            return self.vote(user_id, target_name)
        
        if text == "انهاء التصويت":
            if self.phase == "voting":
                return self.end_voting()
            return {"response": self.simple_message("ليس وقت التصويت الآن")}
        
        # اوامر الادوار الخاصة
        if text == "اقتل" or text.startswith("اقتل "):
            return self.mafia_action(
                user_id,
                text.replace("اقتل ", "").strip() if " " in text else ""
            )
        
        if text == "افحص" or text.startswith("افحص "):
            return self.detective_action(
                user_id,
                text.replace("افحص ", "").strip() if " " in text else ""
            )
        
        if text == "احمي" or text.startswith("احمي "):
            return self.doctor_action(
                user_id,
                text.replace("احمي ", "").strip() if " " in text else ""
            )
        
        return None
    
    def mafia_action(self, user_id, target_name):
        """اجراء المافيا"""
        if user_id not in self.players or self.players[user_id]['role'] != 'mafia':
            return {"response": self.simple_message("انت لست المافيا")}
        
        if self.phase != "night":
            return {"response": self.simple_message("ليس وقت الليل الآن")}
        
        c = self.get_theme_colors()
        alive = [(uid, p) for uid, p in self.players.items() if p['alive'] and uid != user_id]
        
        if target_name:
            for uid, p in self.players.items():
                if p['name'] == target_name and p['alive'] and uid != user_id:
                    self.night_actions['mafia_target'] = uid
                    return {"response": self.simple_message(f"تم اختيار {target_name} للقتل")}
            return {"response": self.simple_message("لا يوجد لاعب حي بهذا الاسم")}
        
        # عرض قائمة بالأزرار
        buttons = []
        for uid, p in alive:
            buttons.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": p['name'],
                    "text": f"اقتل {p['name']}"
                },
                "style": "primary",
                "color": "#F8FBFC",
                "height": "sm"
            })
        
        if not buttons:
            return {"response": self.simple_message("لا يوجد اهداف متاحة")}
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "اختر من تريد قتله",
                        "size": "lg",
                        "weight": "bold",
                        "color": c["text"],
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": c["border"]
                    },
                    {
                        "type": "text",
                        "text": "اختر لاعب من القائمة",
                        "size": "sm",
                        "color": c["text2"],
                        "align": "center",
                        "margin": "lg"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": buttons
            }
        }
        
        return {"response": FlexMessage(alt_text="اختر الهدف", contents=FlexContainer.from_dict(bubble))}
    
    def detective_action(self, user_id, target_name):
        """اجراء المحقق"""
        if user_id not in self.players or self.players[user_id]['role'] != 'detective':
            return {"response": self.simple_message("انت لست المحقق")}
        
        if self.phase != "night":
            return {"response": self.simple_message("ليس وقت الليل الآن")}
        
        c = self.get_theme_colors()
        alive = [(uid, p) for uid, p in self.players.items() if p['alive'] and uid != user_id]
        
        if target_name:
            for uid, p in self.players.items():
                if p['name'] == target_name and p['alive'] and uid != user_id:
                    role = p['role']
                    result = "مافيا" if role == 'mafia' else "بريء"
                    
                    bubble = {
                        "type": "bubble",
                        "size": "mega",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "backgroundColor": c["bg"],
                            "paddingAll": "20px",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "نتيجة الفحص",
                                    "size": "xl",
                                    "weight": "bold",
                                    "color": c["text"],
                                    "align": "center"
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
                                    "cornerRadius": "8px",
                                    "paddingAll": "15px",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": target_name,
                                            "size": "lg",
                                            "weight": "bold",
                                            "color": c["text"],
                                            "align": "center"
                                        },
                                        {
                                            "type": "text",
                                            "text": result,
                                            "size": "xxl",
                                            "weight": "bold",
                                            "color": c["text"],
                                            "align": "center",
                                            "margin": "md"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                    
                    return {"response": FlexMessage(alt_text="نتيجة الفحص", contents=FlexContainer.from_dict(bubble))}
            return {"response": self.simple_message("لا يوجد لاعب حي بهذا الاسم")}
        
        # عرض قائمة بالأزرار
        buttons = []
        for uid, p in alive:
            buttons.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": p['name'],
                    "text": f"افحص {p['name']}"
                },
                "style": "primary",
                "color": "#F8FBFC",
                "height": "sm"
            })
        
        if not buttons:
            return {"response": self.simple_message("لا يوجد اهداف متاحة")}
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "اختر من تريد فحصه",
                        "size": "lg",
                        "weight": "bold",
                        "color": c["text"],
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": c["border"]
                    },
                    {
                        "type": "text",
                        "text": "اختر لاعب من القائمة",
                        "size": "sm",
                        "color": c["text2"],
                        "align": "center",
                        "margin": "lg"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": buttons
            }
        }
        
        return {"response": FlexMessage(alt_text="اختر من تريد فحصه", contents=FlexContainer.from_dict(bubble))}
    
    def doctor_action(self, user_id, target_text):
        """اجراء الدكتور"""
        if user_id not in self.players or self.players[user_id]['role'] != 'doctor':
            return {"response": self.simple_message("انت لست الدكتور")}
        
        if self.phase != "night":
            return {"response": self.simple_message("ليس وقت الليل الآن")}
        
        c = self.get_theme_colors()
        alive = [(uid, p) for uid, p in self.players.items() if p['alive']]
        
        if target_text:
            if target_text == "نفسي":
                self.night_actions['doctor_target'] = user_id
                return {"response": self.simple_message("تم حماية نفسك")}
            
            for uid, p in self.players.items():
                if p['name'] == target_text and p['alive']:
                    self.night_actions['doctor_target'] = uid
                    return {"response": self.simple_message(f"تم حماية {target_text}")}
            return {"response": self.simple_message("لا يوجد لاعب حي بهذا الاسم")}
        
        # عرض قائمة بالأزرار
        buttons = [
            {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": "احمي نفسي",
                    "text": "احمي نفسي"
                },
                "style": "primary",
                "color": "#F8FBFC",
                "height": "sm"
            }
        ]
        
        for uid, p in alive:
            if uid != user_id:
                buttons.append({
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": p['name'],
                        "text": f"احمي {p['name']}"
                    },
                    "style": "primary",
                    "color": "#F8FBFC",
                    "height": "sm"
                })
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "اختر من تريد حمايته",
                        "size": "lg",
                        "weight": "bold",
                        "color": c["text"],
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": c["border"]
                    },
                    {
                        "type": "text",
                        "text": "اختر لاعب من القائمة",
                        "size": "sm",
                        "color": c["text2"],
                        "align": "center",
                        "margin": "lg"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": buttons
            }
        }
        
        return {"response": FlexMessage(alt_text="اختر من تريد حمايته", contents=FlexContainer.from_dict(bubble))}("\n".join(result_parts)),
                    self.winner_message(winner)
                ],
                "game_over": True
            }
        
        self.phase = "day"
        return {
            "response": [
                self.simple_message("\n".join(result_parts)),
                self.day_message()
            ]
        }

    def day_message(self):
        """رسالة مرحلة النهار"""
        c = self.get_theme_colors()
        alive = [p for p in self.players.values() if p['alive']]
        
        alive_list = []
        for i, p in enumerate(alive, 1):
            alive_list.append({
                "type": "text",
                "text": f"{i}. {p['name']}",
                "size": "sm",
                "color": c["text"],
                "margin": "xs" if i > 1 else "md"
            })
        
        contents = [
            {
                "type": "text",
                "text": f"النهار - اليوم {self.day_number}",
                "size": "xl",
                "weight": "bold",
                "color": c["text"],
                "align": "center"
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
                "cornerRadius": "8px",
                "paddingAll": "12px",
                "contents": [
                    {
                        "type": "text",
                        "text": "وقت النقاش والتصويت",
                        "size": "sm",
                        "color": c["text2"],
                        "align": "center"
                    }
                ]
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "contents": [
                    {
                        "type": "text",
                        "text": "الاحياء:",
                        "size": "sm",
                        "weight": "bold",
                        "color": c["text"]
                    }
                ] + alive_list
            },
            {
                "type": "separator",
                "margin": "lg",
                "color": c["border"]
            }
        ]
        
        footer = {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "action": {"type": "message", "label": "بدء التصويت", "text": "تصويت مافيا"},
                    "style": "primary",
                    "color": "#F8FBFC",
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {"type": "message", "label": "حالة اللعبة", "text": "حالة مافيا"},
                    "style": "secondary",
                    "color": "#F8FBFC",
                    "height": "sm"
                }
            ]
        }
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": footer
        }
        
        return FlexMessage(alt_text="مافيا - النهار", contents=FlexContainer.from_dict(bubble))

    def voting_message(self):
        """رسالة التصويت"""
        c = self.get_theme_colors()
        alive = [(uid, p) for uid, p in self.players.items() if p['alive']]
        
        vote_buttons = []
        for uid, p in alive:
            vote_buttons.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": p['name'],
                    "text": f"صوت {p['name']}"
                },
                "style": "primary",
                "color": "#F8FBFC",
                "height": "sm"
            })
        
        vote_list = []
        if self.votes:
            vote_counts = {}
            for target_name in self.votes.values():
                vote_counts[target_name] = vote_counts.get(target_name, 0) + 1
            
            for target_name, count in sorted(vote_counts.items(), key=lambda x: x[1], reverse=True):
                vote_list.append({
                    "type": "text",
                    "text": f"{target_name}: {count} صوت",
                    "size": "sm",
                    "color": c["text"],
                    "margin": "xs"
                })
        
        if not vote_list:
            vote_list = [{
                "type": "text",
                "text": "لا توجد اصوات بعد",
                "size": "xs",
                "color": c["text2"],
                "margin": "md"
            }]
        
        contents = [
            {
                "type": "text",
                "text": "التصويت",
                "size": "xl",
                "weight": "bold",
                "color": c["text"],
                "align": "center"
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
                "cornerRadius": "8px",
                "paddingAll": "12px",
                "contents": [
                    {
                        "type": "text",
                        "text": "اختر من تريد طرده",
                        "size": "sm",
                        "color": c["text2"],
                        "align": "center"
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
                "margin": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "الاصوات الحالية:",
                        "size": "sm",
                        "weight": "bold",
                        "color": c["text"]
                    }
                ] + vote_list
            },
            {
                "type": "separator",
                "margin": "lg",
                "color": c["border"]
            }
        ]
        
        footer_contents = vote_buttons + [
            {"type": "separator", "margin": "sm"},
            {
                "type": "button",
                "action": {"type": "message", "label": "انهاء التصويت", "text": "انهاء التصويت"},
                "style": "primary",
                "color": "#F8FBFC",
                "height": "sm"
            }
        ]
        
        footer = {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": footer_contents
        }
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            },
            "footer": footer
        }
        
        return FlexMessage(alt_text="مافيا - التصويت", contents=FlexContainer.from_dict(bubble))

    def vote(self, user_id, target_name):
        """تسجيل صوت لاعب"""
        if self.phase != "voting":
            return {"response": self.simple_message("ليس وقت التصويت الآن")}
        
        if user_id not in self.players or not self.players[user_id]['alive']:
            return {"response": self.simple_message("انت لست في اللعبة او انت ميت")}
        
        for uid, p in self.players.items():
            if p['name'] == target_name and p['alive']:
                self.votes[user_id] = target_name
                return {
                    "response": [
                        self.simple_message(f"تم تسجيل صوتك لـ {target_name}"),
                        self.voting_message()
                    ]
                }
        
        return {"response": self.simple_message("لا يوجد لاعب حي بهذا الاسم")}

    def end_voting(self):
        """انهاء التصويت واعلان النتيجة"""
        if not self.votes:
            return {"response": self.simple_message("لا توجد اصوات للعد")}
        
        vote_counts = {}
        for target_name in self.votes.values():
            vote_counts[target_name] = vote_counts.get(target_name, 0) + 1
        
        max_votes = max(vote_counts.values())
        eliminated = [name for name, count in vote_counts.items() if count == max_votes]
        
        if len(eliminated) > 1:
            result_parts = [
                f"تعادل في الاصوات بين:",
                ", ".join(eliminated),
                "لا احد تم طرده"
            ]
        else:
            eliminated_name = eliminated[0]
            for uid, p in self.players.items():
                if p['name'] == eliminated_name:
                    self.players[uid]['alive'] = False
                    role_names = {
                        'mafia': 'مافيا',
                        'detective': 'محقق',
                        'doctor': 'دكتور',
                        'citizen': 'مواطن'
                    }
                    role_name = role_names[p['role']]
                    result_parts = [
                        f"تم طرد: {eliminated_name}",
                        f"الدور: {role_name}"
                    ]
                    break
        
        self.votes = {}
        winner = self.check_winner()
        
        if winner:
            return {
                "response": [
                    self.simple_message
