from linebot.v3.messaging import (
    TextMessage, FlexMessage, FlexContainer, PushMessageRequest
)
import random
import time
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
        
        # بيانات اللعبة
        self.players = {}
        self.phase = "registration"
        self.day_number = 0
        self.night_actions = {
            'mafia_target': None,
            'doctor_target': None,
            'detective_check': None
        }
        self.votes = {}
        self.min_players = 4
        self.created_at = time.time()
    
    def start_game(self):
        """بدء اللعبة"""
        self.phase = "registration"
        self.players = {}
        self.votes = {}
        self.night_actions = {
            'mafia_target': None,
            'doctor_target': None,
            'detective_check': None
        }
        self.day_number = 0
        self.game_active = True
        return self.registration_message()
    
    def get_question(self):
        """عرض شاشة التسجيل"""
        return self.registration_message()
    
    # =====================================================
    # شاشة التسجيل
    # =====================================================
    def registration_message(self):
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
        
        contents = [
            {
                "type": "text",
                "text": "لعبة المافيا",
                "size": "xl",
                "weight": "bold",
                "color": c["primary"],
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
                        "text": "شرح الادوار",
                        "size": "md",
                        "weight": "bold",
                        "color": c["text"]
                    },
                    {
                        "type": "text",
                        "text": "المافيا: يقتلون شخص كل ليلة",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "sm"
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
                        "text": "المحقق: يفحص شخص ليعرف دوره",
                        "size": "xs",
                        "color": c["text2"],
                        "wrap": True,
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": "المواطنون: يصوتون على المشتبه به نهارا",
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
                                "text": f"{len(self.players)}/{self.min_players}",
                                "size": "xl",
                                "weight": "bold",
                                "color": c["success"] if len(self.players) >= self.min_players else c["text"],
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
                        "text": "المنضمون:",
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
            }
        ]
        
        footer = {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "paddingAll": "12px",
            "backgroundColor": c["card"],
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "انضم للعبة",
                        "text": "انضم مافيا"
                    },
                    "style": "primary",
                    "color": c["success"],
                    "height": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "ابدا اللعبة",
                        "text": "بدء مافيا"
                    },
                    "style": "primary",
                    "color": c["accent"],
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
                    "color": self.BUTTON_COLOR,
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
        
        return FlexMessage(
            alt_text="لعبة المافيا",
            contents=FlexContainer.from_dict(bubble)
        )
    
    # =====================================================
    # اضافة لاعب
    # =====================================================
    def add_player(self, user_id, name):
        if self.phase != "registration":
            return {"response": self.build_text_message("اللعبة بدأت بالفعل")}
        
        if user_id in self.players:
            return {"response": self.build_text_message("انت مسجل بالفعل")}
        
        self.players[user_id] = {
            'name': name,
            'role': None,
            'alive': True
        }
        
        return {"response": self.registration_message()}
    
    # =====================================================
    # توزيع الادوار
    # =====================================================
    def assign_roles(self):
        if len(self.players) < self.min_players:
            return {
                "response": self.build_text_message(
                    f"عدد اللاعبين غير كاف\nيجب {self.min_players} لاعبين على الاقل"
                )
            }
        
        player_ids = list(self.players.keys())
        random.shuffle(player_ids)
        
        # توزيع الادوار
        roles = ['mafia', 'detective', 'doctor'] + ['citizen'] * (len(player_ids) - 3)
        
        for uid, role in zip(player_ids, roles):
            self.players[uid]['role'] = role
            self.send_role_private(uid, role)
        
        self.phase = "night"
        self.day_number = 1
        
        return {
            "response": [
                self.build_text_message("تم توزيع الادوار في الخاص"),
                self.night_message()
            ]
        }
    
    # =====================================================
    # ارسال الدور للاعب
    # =====================================================
    def send_role_private(self, user_id, role):
        role_info = {
            'mafia': {
                'title': 'انت المافيا',
                'desc': 'دورك: اختيار شخص للقتل كل ليلة',
                'color': '#DC2626'
            },
            'detective': {
                'title': 'انت المحقق',
                'desc': 'دورك: فحص شخص واحد كل ليلة لمعرفة دوره',
                'color': '#2563EB'
            },
            'doctor': {
                'title': 'انت الدكتور',
                'desc': 'دورك: حماية شخص واحد كل ليلة من القتل',
                'color': '#16A34A'
            },
            'citizen': {
                'title': 'انت مواطن',
                'desc': 'دورك: المشاركة في التصويت النهاري',
                'color': '#6B7280'
            }
        }
        
        info = role_info[role]
        c = self.get_theme_colors()
        
        contents = [
            {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": info['color'],
                "cornerRadius": "8px",
                "paddingAll": "16px",
                "contents": [
                    {
                        "type": "text",
                        "text": "Bot 65",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#FFFFFF",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "دورك السري",
                        "size": "md",
                        "color": "#FFFFFF",
                        "align": "center",
                        "margin": "xs"
                    }
                ]
            },
            {
                "type": "text",
                "text": info['title'],
                "size": "xxl",
                "weight": "bold",
                "color": c["text"],
                "align": "center",
                "margin": "lg"
            },
            {
                "type": "separator",
                "margin": "md",
                "color": c["border"]
            },
            {
                "type": "text",
                "text": info['desc'],
                "size": "sm",
                "color": c["text2"],
                "wrap": True,
                "align": "center",
                "margin": "md"
            }
        ]
        
        if role != 'citizen':
            contents.append({
                "type": "text",
                "text": "ستصلك نافذة الاختيار قريبا",
                "size": "xs",
                "color": c["text3"],
                "align": "center",
                "margin": "md"
            })
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px",
                "backgroundColor": c["bg"]
            }
        }
        
        try:
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[FlexMessage(
                        alt_text="دورك في اللعبة",
                        contents=FlexContainer.from_dict(bubble)
                    )]
                )
            )
            
            # ارسال ازرار الاختيار للادوار النشطة
            if role != 'citizen':
                time.sleep(1)
                self.send_action_buttons(user_id, role)
                
        except Exception as e:
            logger.error(f"خطأ في ارسال الدور للاعب {user_id}: {e}")
    
    # =====================================================
    # ارسال ازرار الاختيار
    # =====================================================
    def send_action_buttons(self, user_id, role):
        alive_others = [
            (uid, p['name']) 
            for uid, p in self.players.items() 
            if p['alive'] and uid != user_id
        ]
        
        role_config = {
            'mafia': {
                'title': 'اختر من تريد قتله',
                'action': 'اقتل',
                'color': '#DC2626'
            },
            'detective': {
                'title': 'اختر من تريد فحصه',
                'action': 'افحص',
                'color': '#2563EB'
            },
            'doctor': {
                'title': 'اختر من تريد حمايته',
                'action': 'احمي',
                'color': '#16A34A'
            }
        }
        
        config = role_config.get(role, {})
        c = self.get_theme_colors()
        buttons = []
        
        # الدكتور يمكنه حماية نفسه
        if role == 'doctor':
            buttons.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": "احمي نفسي",
                    "text": f"{config['action']} نفسي"
                },
                "style": "primary",
                "color": config['color'],
                "height": "sm"
            })
        
        # اضافة باقي اللاعبين (اول 10)
        for uid, name in alive_others[:10]:
            buttons.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": name,
                    "text": f"{config['action']} {name}"
                },
                "style": "secondary",
                "color": self.BUTTON_COLOR,
                "height": "sm",
                "margin": "xs"
            })
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": config['color'],
                        "cornerRadius": "8px",
                        "paddingAll": "12px",
                        "contents": [
                            {
                                "type": "text",
                                "text": config['title'],
                                "size": "md",
                                "color": "#FFFFFF",
                                "align": "center",
                                "wrap": True
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": f"اللاعبون الاحياء ({len(alive_others) + 1})",
                        "size": "sm",
                        "weight": "bold",
                        "color": c["text"],
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "xs",
                        "margin": "md",
                        "contents": buttons
                    }
                ]
            }
        }
        
        try:
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[FlexMessage(
                        alt_text="اختر هدفك",
                        contents=FlexContainer.from_dict(bubble)
                    )]
                )
            )
        except Exception as e:
            logger.error(f"خطأ في ارسال ازرار الاختيار: {e}")
    
    # =====================================================
    # شاشة الليل
    # =====================================================
    def night_message(self):
        c = self.get_theme_colors()
        alive = sum(1 for p in self.players.values() if p['alive'])
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": c["primary"],
                        "cornerRadius": "8px",
                        "paddingAll": "16px",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"اليوم {self.day_number} - الليل",
                                "size": "lg",
                                "weight": "bold",
                                "color": c["bg"],
                                "align": "center"
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": "الليل حل - الادوار تعمل الان",
                        "size": "md",
                        "color": c["text"],
                        "align": "center",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": f"اللاعبون الاحياء: {alive}",
                        "size": "sm",
                        "color": c["text2"],
                        "align": "center",
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": c["border"]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "انهاء الليل",
                                    "text": "انهاء الليل"
                                },
                                "style": "primary",
                                "color": c["accent"],
                                "height": "sm"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "حالة اللعبة",
                                    "text": "حالة مافيا"
                                },
                                "style": "secondary",
                                "color": self.BUTTON_COLOR,
                                "height": "sm"
                            }
                        ]
                    }
                ]
            }
        }
        
        return FlexMessage(
            alt_text="مرحلة الليل",
            contents=FlexContainer.from_dict(bubble)
        )
    
    # =====================================================
    # معالجة نهاية الليل
    # =====================================================
    def process_night(self):
        mafia_target = self.night_actions.get('mafia_target')
        doctor_target = self.night_actions.get('doctor_target')
        messages = []
        
        # التحقق من القتل والحماية
        if mafia_target and mafia_target != doctor_target and mafia_target in self.players:
            self.players[mafia_target]['alive'] = False
            victim_name = self.players[mafia_target]['name']
            messages.append(f"طلع النهار - تم قتل {victim_name}")
        else:
            messages.append("طلع النهار - لم يقتل احد الليلة")
        
        # اعادة تعيين اجراءات الليل
        self.night_actions = {
            'mafia_target': None,
            'doctor_target': None,
            'detective_check': None
        }
        self.phase = "day"
        
        # التحقق من الفائز
        winner = self.check_winner()
        if winner:
            return winner
        
        # ارسال الرسائل
        response_messages = [
            self.build_text_message(msg) for msg in messages
        ]
        response_messages.append(self.day_message())
        
        return {"response": response_messages}
    
    # =====================================================
    # شاشة النهار
    # =====================================================
    def day_message(self):
        c = self.get_theme_colors()
        alive = sum(1 for p in self.players.values() if p['alive'])
        warning_color = c.get("warning", c.get("accent", "#F59E0B"))
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": warning_color,
                        "cornerRadius": "8px",
                        "paddingAll": "16px",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"اليوم {self.day_number} - النهار",
                                "size": "lg",
                                "weight": "bold",
                                "color": "#FFFFFF",
                                "align": "center"
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": "وقت المناقشة والتصويت",
                        "size": "md",
                        "color": c["text"],
                        "align": "center",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": f"اللاعبون الاحياء: {alive}",
                        "size": "sm",
                        "color": c["text2"],
                        "align": "center",
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": c["border"]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "بدء التصويت",
                                    "text": "تصويت مافيا"
                                },
                                "style": "primary",
                                "color": c["accent"],
                                "height": "sm"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "حالة اللعبة",
                                    "text": "حالة مافيا"
                                },
                                "style": "secondary",
                                "color": self.BUTTON_COLOR,
                                "height": "sm"
                            }
                        ]
                    }
                ]
            }
        }
        
        return FlexMessage(
            alt_text="مرحلة النهار",
            contents=FlexContainer.from_dict(bubble)
        )
    
    # =====================================================
    # شاشة التصويت
    # =====================================================
    def voting_message(self):
        c = self.get_theme_colors()
        alive = [
            (uid, p['name']) 
            for uid, p in self.players.items() 
            if p['alive']
        ]
        buttons = []
        
        for uid, name in alive[:10]:
            buttons.append({
                "type": "button",
                "action": {
                    "type": "message",
                    "label": name,
                    "text": f"صوت {name}"
                },
                "style": "secondary",
                "color": self.BUTTON_COLOR,
                "height": "sm",
                "margin": "xs" if buttons else "none"
            })
        
        buttons.append({
            "type": "button",
            "action": {
                "type": "message",
                "label": "انهاء التصويت",
                "text": "انهاء التصويت"
            },
            "style": "primary",
            "color": c.get("error", c["primary"]),
            "height": "sm",
            "margin": "md"
        })
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": [
                    {
                        "type": "text",
                        "text": "التصويت",
                        "size": "xl",
                        "weight": "bold",
                        "color": c["primary"],
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "اضغط على اسم من تظنه المافيا",
                        "size": "sm",
                        "color": c["text2"],
                        "align": "center",
                        "wrap": True,
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": c["border"]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "xs",
                        "margin": "lg",
                        "contents": buttons
                    }
                ]
            }
        }
        
        return FlexMessage(
            alt_text="التصويت",
            contents=FlexContainer.from_dict(bubble)
        )
    
    # =====================================================
    # معالجة التصويت
    # =====================================================
    def vote(self, user_id, target_name):
        if self.phase != "voting":
            return {"response": self.build_text_message("ليس وقت التصويت")}
        
        if user_id not in self.players or not self.players[user_id]['alive']:
            return {"response": self.build_text_message("لا يمكنك التصويت")}
        
        for uid, p in self.players.items():
            if p['name'] == target_name and p['alive']:
                self.votes[user_id] = uid
                return {"response": self.build_text_message(f"تم تصويتك لـ {target_name}")}
        
        return {"response": self.build_text_message("لا يوجد لاعب بهذا الاسم")}
    
    # =====================================================
    # انهاء التصويت
    # =====================================================
    def end_voting(self):
        if not self.votes:
            self.phase = "night"
            self.day_number += 1
            return {
                "response": [
                    self.build_text_message("لم يتم التصويت"),
                    self.night_message()
                ]
            }
        
        # حساب الاصوات
        vote_counts = {}
        for target_uid in self.votes.values():
            vote_counts[target_uid] = vote_counts.get(target_uid, 0) + 1
        
        # اللاعب الاكثر اصوات
        killed_uid = max(vote_counts, key=vote_counts.get)
        self.players[killed_uid]['alive'] = False
        killed_name = self.players[killed_uid]['name']
        
        # اعادة تعيين
        self.votes = {}
        self.phase = "night"
        self.day_number += 1
        
        # التحقق من الفائز
        winner = self.check_winner()
        if winner:
            return winner
        
        return {
            "response": [
                self.build_text_message(f"تم اعدام {killed_name} بالتصويت"),
                self.night_message()
            ]
        }
    
    # =====================================================
    # التحقق من الفائز
    # =====================================================
    def check_winner(self):
        mafia_count = sum(
            1 for p in self.players.values() 
            if p['alive'] and p['role'] == 'mafia'
        )
        citizen_count = sum(
            1 for p in self.players.values() 
            if p['alive'] and p['role'] != 'mafia'
        )
        
        if mafia_count == 0:
            self.phase = "ended"
            self.game_active = False
            return {
                "response": self.winner_message("المواطنون"),
                "game_over": True
            }
        
        if mafia_count >= citizen_count:
            self.phase = "ended"
            self.game_active = False
            return {
                "response": self.winner_message("المافيا"),
                "game_over": True
            }
        
        return None
    
    # =====================================================
    # شاشة الفائز
    # =====================================================
    def winner_message(self, winner_team):
        c = self.get_theme_colors()
        
        bubble = {
            "type": "bubble",
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
                        "color": c["primary"],
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": c["border"]
                    },
                    {
                        "type": "text",
                        "text": "الفائز",
                        "size": "sm",
                        "color": c["text2"],
                        "align": "center",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": winner_team,
                        "size": "xxl",
                        "weight": "bold",
                        "color": c["success"],
                        "align": "center",
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": c["border"]
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "لعبة جديدة",
                            "text": "مافيا"
                        },
                        "style": "primary",
                        "color": c["accent"],
                        "height": "sm",
                        "margin": "lg"
                    }
                ]
            }
        }
        
        return FlexMessage(
            alt_text="نهاية اللعبة",
            contents=FlexContainer.from_dict(bubble)
        )
    
    # =====================================================
    # شاشة حالة اللعبة
    # =====================================================
    def status_message(self):
        c = self.get_theme_colors()
        alive = [p for p in self.players.values() if p['alive']]
        dead = [p for p in self.players.values() if not p['alive']]
        
        alive_list = [
            {
                "type": "text",
                "text": f"{i}. {p['name']}",
                "size": "sm",
                "color": c["text"],
                "margin": "xs" if i > 1 else "md"
            }
            for i, p in enumerate(alive, 1)
        ]
        
        dead_list = [
            {
                "type": "text",
                "text": f"{i}. {p['name']}",
                "size": "sm",
                "color": c["text2"],
                "margin": "xs" if i > 1 else "md"
            }
            for i, p in enumerate(dead, 1)
        ]
        
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
                        "color": c["primary"],
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": c["border"]
                    },
                    {
                        "type": "text",
                        "text": f"اليوم: {self.day_number}",
                        "size": "md",
                        "weight": "bold",
                        "color": c["text"],
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": f"المرحلة: {phase_names.get(self.phase, self.phase)}",
                        "size": "sm",
                        "color": c["text2"],
                        "margin": "xs"
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
                                "text": "الاحياء",
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
                                "text": "المقتولون",
                                "size": "md",
                                "weight": "bold",
                                "color": c["text"]
                            }
                        ] + dead_list
                    }
                ]
            }
        }
        
        return FlexMessage(
            alt_text="حالة اللعبة",
            contents=FlexContainer.from_dict(bubble)
        )
    
    # =====================================================
    # معالجة الاوامر
    # =====================================================
    def check_answer(self, text, user_id, display_name):
        text = text.strip()
        
        # الانضمام للعبة
        if text == "انضم مافيا":
            return self.add_player(user_id, display_name)
        
        # بدء اللعبة
        if text == "بدء مافيا":
            return self.assign_roles()
        
        # حالة اللعبة
        if text == "حالة مافيا":
            return {"response": self.status_message()}
        
        # الغاء اللعبة
        if text == "الغاء مافيا":
            if self.phase == "registration":
                self.game_active = False
                return {"response": self.build_text_message("تم الغاء اللعبة")}
            return {"response": self.build_text_message("لا يمكن الالغاء بعد بدء اللعبة")}
        
        # انهاء الليل
        if text == "انهاء الليل":
            if self.phase == "night":
                return self.process_night()
            return {"response": self.build_text_message("ليس وقت الليل")}
        
        # بدء التصويت
        if text == "تصويت مافيا":
            if self.phase in ["day", "voting"]:
                self.phase = "voting"
                return {"response": self.voting_message()}
            return {"response": self.build_text_message("ليس وقت التصويت")}
        
        # التصويت على شخص
        if text.startswith("صوت "):
            target_name = text.replace("صوت ", "").strip()
            return self.vote(user_id, target_name)
        
        # انهاء التصويت
        if text == "انهاء التصويت":
            if self.phase == "voting":
                return self.end_voting()
            return {"response": self.build_text_message("ليس وقت التصويت")}
        
        # اجراءات المافيا
        if text.startswith("اقتل "):
            if user_id not in self.players or self.players[user_id]['role'] != 'mafia':
                return {"response": self.build_text_message("انت لست المافيا")}
            if self.phase != "night":
                return {"response": self.build_text_message("ليس وقت الليل")}
            
            target_name = text.replace("اقتل ", "").strip()
            for uid, p in self.players.items():
                if p['name'] == target_name and p['alive'] and uid != user_id:
                    self.night_actions['mafia_target'] = uid
                    return {"response": self.build_text_message(f"تم اختيار {target_name} للقتل")}
            return {"response": self.build_text_message("لا يوجد لاعب بهذا الاسم")}
        
        # اجراءات المحقق
        if text.startswith("افحص "):
            if user_id not in self.players or self.players[user_id]['role'] != 'detective':
                return {"response": self.build_text_message("انت لست المحقق")}
            if self.phase != "night":
                return {"response": self.build_text_message("ليس وقت الليل")}
            
            target_name = text.replace("افحص ", "").strip()
            for uid, p in self.players.items():
                if p['name'] == target_name and p['alive'] and uid != user_id:
                    role = p['role']
                    result = "مافيا" if role == 'mafia' else "بريء"
                    return {"response": self.build_text_message(f"{target_name} هو {result}")}
            return {"response": self.build_text_message("لا يوجد لاعب بهذا الاسم")}
        
        # اجراءات الدكتور
        if text.startswith("احمي "):
            if user_id not in self.players or self.players[user_id]['role'] != 'doctor':
                return {"response": self.build_text_message("انت لست الدكتور")}
            if self.phase != "night":
                return {"response": self.build_text_message("ليس وقت الليل")}
            
            target_text = text.replace("احمي ", "").strip()
            
            # حماية النفس
            if target_text == "نفسي":
                self.night_actions['doctor_target'] = user_id
                return {"response": self.build_text_message("تم حماية نفسك")}
            
            # حماية شخص اخر
            for uid, p in self.players.items():
                if p['name'] == target_text and p['alive']:
                    self.night_actions['doctor_target'] = uid
                    return {"response": self.build_text_message(f"تم حماية {target_text}")}
            
            return {"response": self.build_text_message("لا يوجد لاعب بهذا الاسم")}
        
        return None
