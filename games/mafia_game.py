from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer
import random
from games.base_game import BaseGame
import logging

logger = logging.getLogger(__name__)

class MafiaGame(BaseGame):
    """لعبة المافيا - لعبة جماعية"""
    
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
        self.game_active = False

    def get_question(self):
        """تنفيذ الدالة المطلوبة من BaseGame"""
        return self.registration_message()

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
            player_list = [{"type": "text", "text": "لا يوجد لاعبين", "size": "sm", "color": c["text2"], "align": "center", "margin": "md"}]

        ready_text = "جاهز" if len(self.players) >= self.min_players else f"{len(self.players)}/{self.min_players}"
        start_disabled = len(self.players) < self.min_players
        start_color = c["accent"] if not start_disabled else c.get("border", "#E5E7EB")

        contents = [
            {"type": "text", "text": "لعبة المافيا", "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {"type": "box", "layout": "vertical", "margin": "lg", "backgroundColor": c["card"], "cornerRadius": "8px", "paddingAll": "12px", "contents": [
                {"type": "text", "text": "شرح اللعبة", "size": "md", "weight": "bold", "color": c["text"]},
                {"type": "text", "text": "المافيا: يقتلون ليلا", "size": "xs", "color": c["text2"], "wrap": True, "margin": "sm"},
                {"type": "text", "text": "الدكتور: يحمي شخص", "size": "xs", "color": c["text2"], "wrap": True, "margin": "xs"},
                {"type": "text", "text": "المحقق: يفحص شخص", "size": "xs", "color": c["text2"], "wrap": True, "margin": "xs"},
                {"type": "text", "text": "المواطنون: يصوتون نهارا", "size": "xs", "color": c["text2"], "wrap": True, "margin": "xs"}
            ]},
            {"type": "box", "layout": "horizontal", "margin": "lg", "contents": [
                {"type": "box", "layout": "vertical", "flex": 1, "contents": [
                    {"type": "text", "text": ready_text, "size": "xl", "weight": "bold", 
                     "color": c["success"] if not start_disabled else c["text"], "align": "center"},
                    {"type": "text", "text": "اللاعبون", "size": "xs", "color": c["text2"], "align": "center", "margin": "xs"}
                ]}
            ]},
            {"type": "box", "layout": "vertical", "margin": "lg", "contents": [{"type": "text", "text": "اللاعبون:", "size": "sm", "weight": "bold", "color": c["text"]}] + player_list},
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]

        footer = {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [
            {"type": "button", "action": {"type": "message", "label": "انضم مافيا", "text": "انضم مافيا"}, "style": "primary", "color": c["success"], "height": "sm"},
            {"type": "button", "action": {"type": "message", "label": "بدء مافيا", "text": "بدء مافيا"}, "style": "primary", "color": start_color, "height": "sm"},
            {"type": "button", "action": {"type": "message", "label": "الغاء مافيا", "text": "الغاء مافيا"}, "style": "secondary", "color": self.BUTTON_COLOR, "height": "sm"}
        ]}

        bubble = {"type": "bubble", "size": "mega", "body": {"type": "box", "layout": "vertical", "contents": contents, "paddingAll": "20px", "backgroundColor": c["bg"]}, "footer": footer}
        return FlexMessage(alt_text="لعبة المافيا", contents=FlexContainer.from_dict(bubble))

    def add_player(self, user_id, name):
        if self.phase != "registration":
            return {"response": self.build_text_message("اللعبة بدأت")}
        if user_id in self.players:
            return {"response": self.build_text_message("انت مسجل")}
        self.players[user_id] = {'name': name, 'role': None, 'alive': True}
        return {"response": self.registration_message()}

    def assign_roles(self):
        if len(self.players) < self.min_players:
            return {"response": self.build_text_message(f"عدد اللاعبين غير كاف - {self.min_players} لاعبين مطلوب")}
        
        player_ids = list(self.players.keys())
        random.shuffle(player_ids)
        roles = ['mafia', 'detective', 'doctor'] + ['citizen'] * (len(player_ids) - 3)
        
        for uid, role in zip(player_ids, roles):
            self.players[uid]['role'] = role
            self.send_role_private(uid, role)
        
        self.phase = "night"
        self.day_number = 1
        self.game_active = True
        return {"response": [self.build_text_message("تم توزيع الادوار في الخاص"), self.night_message()]}

    def send_role_private(self, user_id, role):
        role_names = {
            'mafia': 'المافيا',
            'detective': 'المحقق',
            'doctor': 'الدكتور',
            'citizen': 'مواطن'
        }
        role_desc = {
            'mafia': 'دورك: اقتل شخص ليلا - اكتب: اقتل [اسم]',
            'detective': 'دورك: افحص شخص ليلا - اكتب: افحص [اسم]',
            'doctor': 'دورك: احمي شخص ليلا - اكتب: احمي [اسم] او احمي نفسي',
            'citizen': 'دورك: صوت نهارا لطرد المافيا'
        }
        try:
            from linebot.v3.messaging import PushMessageRequest
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=f"دورك: {role_names[role]}\n{role_desc[role]}")]
                )
            )
        except Exception as e:
            logger.error(f"Failed to send role to {user_id}: {e}")

    def night_message(self):
        c = self.get_theme_colors()
        alive = [p for p in self.players.values() if p['alive']]
        
        alive_list = [{"type": "text", "text": f"{i}. {p['name']}", "size": "sm", "color": c["text"], "margin": "xs" if i > 1 else "md"} for i, p in enumerate(alive, 1)]
        
        contents = [
            {"type": "text", "text": f"الليل - اليوم {self.day_number}", "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {"type": "text", "text": "المافيا والمحقق والدكتور يعملون", "size": "sm", "color": c["text2"], "align": "center", "margin": "lg"},
            {"type": "box", "layout": "vertical", "margin": "lg", "contents": [{"type": "text", "text": "الاحياء:", "size": "sm", "weight": "bold", "color": c["text"]}] + alive_list},
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        footer = {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [
            {"type": "button", "action": {"type": "message", "label": "انهاء الليل", "text": "انهاء الليل"}, "style": "primary", "color": c["accent"], "height": "sm"},
            {"type": "button", "action": {"type": "message", "label": "حالة مافيا", "text": "حالة مافيا"}, "style": "secondary", "color": self.BUTTON_COLOR, "height": "sm"}
        ]}
        
        bubble = {"type": "bubble", "size": "mega", "body": {"type": "box", "layout": "vertical", "contents": contents, "paddingAll": "20px", "backgroundColor": c["bg"]}, "footer": footer}
        return FlexMessage(alt_text="مافيا - الليل", contents=FlexContainer.from_dict(bubble))

    def process_night(self):
        victim_id = self.night_actions['mafia_target']
        saved_id = self.night_actions['doctor_target']
        
        result_text = f"انتهى الليل {self.day_number}\n"
        
        if victim_id and victim_id != saved_id:
            self.players[victim_id]['alive'] = False
            result_text += f"تم قتل: {self.players[victim_id]['name']}\n"
        elif victim_id and victim_id == saved_id:
            result_text += "الدكتور انقذ الضحية\n"
        else:
            result_text += "لم يحدث قتل\n"
        
        self.night_actions = {'mafia_target': None, 'doctor_target': None, 'detective_check': None}
        
        winner = self.check_winner()
        if winner:
            return {"response": self.winner_message(winner), "game_over": True}
        
        self.phase = "day"
        return {"response": [self.build_text_message(result_text), self.day_message()]}

    def day_message(self):
        c = self.get_theme_colors()
        alive = [p for p in self.players.values() if p['alive']]
        
        alive_list = [{"type": "text", "text": f"{i}. {p['name']}", "size": "sm", "color": c["text"], "margin": "xs" if i > 1 else "md"} for i, p in enumerate(alive, 1)]
        
        contents = [
            {"type": "text", "text": f"النهار - اليوم {self.day_number}", "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {"type": "text", "text": "وقت النقاش والتصويت", "size": "sm", "color": c["text2"], "align": "center", "margin": "lg"},
            {"type": "box", "layout": "vertical", "margin": "lg", "contents": [{"type": "text", "text": "الاحياء:", "size": "sm", "weight": "bold", "color": c["text"]}] + alive_list},
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        footer = {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [
            {"type": "button", "action": {"type": "message", "label": "تصويت مافيا", "text": "تصويت مافيا"}, "style": "primary", "color": c["accent"], "height": "sm"},
            {"type": "button", "action": {"type": "message", "label": "حالة مافيا", "text": "حالة مافيا"}, "style": "secondary", "color": self.BUTTON_COLOR, "height": "sm"}
        ]}
        
        bubble = {"type": "bubble", "size": "mega", "body": {"type": "box", "layout": "vertical", "contents": contents, "paddingAll": "20px", "backgroundColor": c["bg"]}, "footer": footer}
        return FlexMessage(alt_text="مافيا - النهار", contents=FlexContainer.from_dict(bubble))

    def voting_message(self):
        c = self.get_theme_colors()
        alive = [p for p in self.players.values() if p['alive']]
        
        alive_list = [{"type": "text", "text": f"{i}. {p['name']}", "size": "sm", "color": c["text"], "margin": "xs" if i > 1 else "md"} for i, p in enumerate(alive, 1)]
        
        vote_list = []
        if self.votes:
            for voter_id, target_name in self.votes.items():
                voter_name = self.players[voter_id]['name']
                vote_list.append({"type": "text", "text": f"{voter_name} صوت لـ {target_name}", "size": "xs", "color": c["text2"], "margin": "xs"})
        
        if not vote_list:
            vote_list = [{"type": "text", "text": "لا توجد اصوات بعد", "size": "xs", "color": c["text3"], "margin": "md"}]
        
        contents = [
            {"type": "text", "text": "التصويت", "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {"type": "text", "text": "صوت بكتابة: صوت [اسم]", "size": "sm", "color": c["text2"], "align": "center", "margin": "lg"},
            {"type": "box", "layout": "vertical", "margin": "lg", "contents": [{"type": "text", "text": "الاحياء:", "size": "sm", "weight": "bold", "color": c["text"]}] + alive_list},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {"type": "box", "layout": "vertical", "margin": "md", "contents": [{"type": "text", "text": "الاصوات:", "size": "sm", "weight": "bold", "color": c["text"]}] + vote_list},
            {"type": "separator", "margin": "lg", "color": c["border"]}
        ]
        
        footer = {"type": "box", "layout": "vertical", "spacing": "sm", "contents": [
            {"type": "button", "action": {"type": "message", "label": "انهاء التصويت", "text": "انهاء التصويت"}, "style": "primary", "color": c["error"], "height": "sm"}
        ]}
        
        bubble = {"type": "bubble", "size": "mega", "body": {"type": "box", "layout": "vertical", "contents": contents, "paddingAll": "20px", "backgroundColor": c["bg"]}, "footer": footer}
        return FlexMessage(alt_text="مافيا - التصويت", contents=FlexContainer.from_dict(bubble))

    def vote(self, user_id, target_name):
        if self.phase != "voting":
            return {"response": self.build_text_message("ليس وقت التصويت")}
        if user_id not in self.players or not self.players[user_id]['alive']:
            return {"response": self.build_text_message("انت لست في اللعبة")}
        
        for uid, p in self.players.items():
            if p['name'] == target_name and p['alive']:
                self.votes[user_id] = target_name
                return {"response": self.build_text_message(f"تم تسجيل صوتك لـ {target_name}")}
        
        return {"response": self.build_text_message("لا يوجد لاعب بهذا الاسم")}

    def end_voting(self):
        if not self.votes:
            return {"response": self.build_text_message("لا توجد اصوات")}
        
        vote_counts = {}
        for target_name in self.votes.values():
            vote_counts[target_name] = vote_counts.get(target_name, 0) + 1
        
        max_votes = max(vote_counts.values())
        eliminated = [name for name, count in vote_counts.items() if count == max_votes]
        
        if len(eliminated) > 1:
            result_text = f"تعادل بين: {', '.join(eliminated)}\nلا احد تم طرده"
        else:
            eliminated_name = eliminated[0]
            for uid, p in self.players.items():
                if p['name'] == eliminated_name:
                    self.players[uid]['alive'] = False
                    role_name = {'mafia': 'مافيا', 'detective': 'محقق', 'doctor': 'دكتور', 'citizen': 'مواطن'}[p['role']]
                    result_text = f"تم طرد: {eliminated_name}\nالدور: {role_name}"
                    break
        
        self.votes = {}
        winner = self.check_winner()
        
        if winner:
            return {"response": [self.build_text_message(result_text), self.winner_message(winner)], "game_over": True}
        
        self.phase = "night"
        self.day_number += 1
        return {"response": [self.build_text_message(result_text), self.night_message()]}

    def check_winner(self):
        alive = [p for p in self.players.values() if p['alive']]
        mafia_count = sum(1 for p in alive if p['role'] == 'mafia')
        citizen_count = len(alive) - mafia_count
        
        if mafia_count == 0:
            return "المواطنون"
        if mafia_count >= citizen_count:
            return "المافيا"
        return None

    def winner_message(self, winner_team):
        c = self.get_theme_colors()
        player_list = [{"type": "text", "text": f"{p['name']} - {p['role']}", "size": "sm", "color": c["text"], "margin": "xs"} for p in self.players.values()]
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": c["bg"],
                "paddingAll": "20px",
                "contents": [
                    {"type": "text", "text": "انتهت اللعبة", "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
                    {"type": "separator", "margin": "md", "color": c["border"]},
                    {"type": "text", "text": "الفائز", "size": "sm", "color": c["text2"], "align": "center", "margin": "lg"},
                    {"type": "text", "text": winner_team, "size": "xxl", "weight": "bold", "color": c["success"], "align": "center", "margin": "sm"},
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {"type": "box", "layout": "vertical", "margin": "lg", "contents": [{"type": "text", "text": "اللاعبون:", "size": "sm", "weight": "bold", "color": c["text"]}] + player_list},
                    {"type": "button", "action": {"type": "message", "label": "اعادة", "text": "مافيا"}, "style": "primary", "color": c["accent"], "height": "sm", "margin": "lg"}
                ]
            }
        }
        
        return FlexMessage(alt_text="نهاية اللعبة", contents=FlexContainer.from_dict(bubble))
    
    def status_message(self):
        c = self.get_theme_colors()
        alive = [p for p in self.players.values() if p['alive']]
        dead = [p for p in self.players.values() if not p['alive']]
        
        alive_list = [{"type": "text", "text": f"{i}. {p['name']}", "size": "sm", "color": c["text"], "margin": "xs" if i > 1 else "md"} for i, p in enumerate(alive, 1)]
        dead_list = [{"type": "text", "text": f"{i}. {p['name']}", "size": "sm", "color": c["text2"], "margin": "xs" if i > 1 else "md"} for i, p in enumerate(dead, 1)]
        
        if not alive_list:
            alive_list = [{"type": "text", "text": "لا يوجد", "size": "sm", "color": c["text2"], "margin": "md"}]
        if not dead_list:
            dead_list = [{"type": "text", "text": "لا يوجد", "size": "sm", "color": c["text2"], "margin": "md"}]
        
        phase_names = {'registration': 'التسجيل', 'night': 'الليل', 'day': 'النهار', 'voting': 'التصويت', 'ended': 'انتهت'}
        
        bubble = {"type": "bubble", "body": {"type": "box", "layout": "vertical", "backgroundColor": c["bg"], "paddingAll": "20px", "contents": [
            {"type": "text", "text": "حالة اللعبة", "size": "xl", "weight": "bold", "color": c["primary"], "align": "center"},
            {"type": "separator", "margin": "md", "color": c["border"]},
            {"type": "text", "text": f"اليوم: {self.day_number}", "size": "md", "weight": "bold", "color": c["text"], "margin": "lg"},
            {"type": "text", "text": f"المرحلة: {phase_names.get(self.phase, self.phase)}", "size": "sm", "color": c["text2"], "margin": "xs"},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "vertical", "margin": "lg", "contents": [{"type": "text", "text": "الاحياء", "size": "md", "weight": "bold", "color": c["text"]}] + alive_list},
            {"type": "separator", "margin": "lg", "color": c["border"]},
            {"type": "box", "layout": "vertical", "margin": "lg", "contents": [{"type": "text", "text": "المقتولون", "size": "md", "weight": "bold", "color": c["text"]}] + dead_list}
        ]}}
        
        return FlexMessage(alt_text="حالة اللعبة", contents=FlexContainer.from_dict(bubble))
    
    def check_answer(self, text, user_id, display_name):
        text = text.strip()
        
        if text == "انضم مافيا":
            return self.add_player(user_id, display_name)
        if text == "بدء مافيا":
            return self.assign_roles()
        if text == "حالة مافيا":
            return {"response": self.status_message()}
        if text == "الغاء مافيا":
            if self.phase == "registration":
                self.game_active = False
                return {"response": self.build_text_message("تم الغاء اللعبة")}
            return {"response": self.build_text_message("لا يمكن الالغاء")}
        if text == "انهاء الليل":
            if self.phase == "night":
                return self.process_night()
            return {"response": self.build_text_message("ليس وقت الليل")}
        if text == "تصويت مافيا":
            if self.phase in ["day", "voting"]:
                self.phase = "voting"
                return {"response": self.voting_message()}
            return {"response": self.build_text_message("ليس وقت التصويت")}
        if text.startswith("صوت "):
            target_name = text.replace("صوت ", "").strip()
            return self.vote(user_id, target_name)
        if text == "انهاء التصويت":
            if self.phase == "voting":
                return self.end_voting()
            return {"response": self.build_text_message("ليس وقت التصويت")}
        if text.startswith("اقتل "):
            if user_id not in self.players or self.players[user_id]['role'] != 'mafia':
                return {"response": self.build_text_message("انت لست المافيا")}
            if self.phase != "night":
                return {"response": self.build_text_message("ليس وقت الليل")}
            target_name = text.replace("اقتل ", "").strip()
            for uid, p in self.players.items():
                if p['name'] == target_name and p['alive'] and uid != user_id:
                    self.night_actions['mafia_target'] = uid
                    return {"response": self.build_text_message(f"تم اختيار {target_name}")}
            return {"response": self.build_text_message("لا يوجد لاعب بهذا الاسم")}
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
        if text.startswith("احمي "):
            if user_id not in self.players or self.players[user_id]['role'] != 'doctor':
                return {"response": self.build_text_message("انت لست الدكتور")}
            if self.phase != "night":
                return {"response": self.build_text_message("ليس وقت الليل")}
            target_text = text.replace("احمي ", "").strip()
            if target_text == "نفسي":
                self.night_actions['doctor_target'] = user_id
                return {"response": self.build_text_message("تم حماية نفسك")}
            for uid, p in self.players.items():
                if p['name'] == target_text and p['alive']:
                    self.night_actions['doctor_target'] = uid
                    return {"response": self.build_text_message(f"تم حماية {target_text}")}
            return {"response": self.build_text_message("لا يوجد لاعب بهذا الاسم")}
        
        return None
