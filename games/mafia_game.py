import random
import time
from collections import Counter
from linebot.v3.messaging import TextMessage, FlexMessage, FlexContainer, PushMessageRequest

class MafiaGame:
    """لعبة المافيا - لعبة جماعية"""
    
    def __init__(self, line_bot_api, theme="light"):
        self.line_bot_api = line_bot_api
        self.theme = theme
        self.game_name = "مافيا"
        self.min_players = 4
        self.max_players = 15
        self.night_timeout = 40
        self.vote_timeout = 40
        self.reset_game()
        
        # ألوان الثيم
        self.themes = {
            "light": {
                "primary": "#1C1C1E",
                "text": "#3C3C43",
                "bg": "#FFFFFF",
                "card": "#F2F2F7",
                "border": "#C6C6C8",
                "button": "#007AFF"
            },
            "dark": {
                "primary": "#F1F5F9",
                "text": "#E5E7EB",
                "bg": "#0F172A",
                "card": "#1E293B",
                "border": "#334155",
                "button": "#60A5FA"
            }
        }

    def reset_game(self):
        """إعادة تعيين حالة اللعبة"""
        self.game_active = False
        self.phase = "lobby"
        self.players = {}
        self.roles = {}
        self.alive_players = set()
        self.dead_players = set()
        self.mafia = set()
        self.doctor = None
        self.detective = None
        self.citizens = set()
        self.night_actions = {}
        self.votes = {}
        self.phase_start_time = None
        self.round_number = 0
        self.withdrawn_users = set()

    def start_game(self):
        """بدء اللعبة"""
        self.game_active = True
        self.phase = "lobby"
        return self._build_lobby_message()
    
    def get_question(self):
        """متطلب من BaseGame - لكن Mafia لا تستخدمه"""
        return self._build_lobby_message()

    def join_player(self, user_id, display_name):
        """انضمام لاعب للعبة"""
        if self.phase != "lobby":
            return TextMessage(text="اللعبة بدأت بالفعل")
        if user_id in self.players:
            return TextMessage(text="أنت منضم مسبقا")
        if len(self.players) >= self.max_players:
            return TextMessage(text="اللعبة ممتلئة")
        self.players[user_id] = {"name": display_name, "alive": True}
        self.alive_players.add(user_id)
        return self._build_lobby_message()

    def _build_lobby_message(self):
        """بناء رسالة اللوبي"""
        count = len(self.players)
        c = self.themes[self.theme]
        player_list = []
        
        if count > 0:
            player_list = [
                {"type": "text", "text": "المنضمون:", "weight": "bold", "size": "sm", "margin": "lg", "color": c["text"]},
                {"type": "separator", "margin": "md", "color": c["border"]}
            ]
            for i, (uid, pdata) in enumerate(self.players.items(), 1):
                player_list.append({
                    "type": "text",
                    "text": f"{i}. {pdata['name']}",
                    "size": "sm",
                    "margin": "sm",
                    "color": c["text"]
                })

        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "backgroundColor": c["bg"],
                "contents": [
                    {"type": "text", "text": "لعبة المافيا", "size": "xxl", "weight": "bold", "align": "center", "color": c["primary"]},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "backgroundColor": c["card"],
                        "cornerRadius": "12px",
                        "paddingAll": "16px",
                        "contents": [
                            {"type": "text", "text": "شرح اللعبة", "weight": "bold", "size": "md", "color": c["primary"]},
                            {"type": "text", "text": "لعبة جماعية تنقسم فيها الأدوار بين المافيا والمواطنين", "size": "xs", "wrap": True, "color": c["text"], "margin": "sm"},
                            {"type": "text", "text": "المافيا: يحاولون قتل المواطنين ليلا", "size": "xs", "wrap": True, "color": c["text"], "margin": "sm"},
                            {"type": "text", "text": "الدكتور: يحمي شخص واحد كل ليلة", "size": "xs", "wrap": True, "color": c["text"], "margin": "xs"},
                            {"type": "text", "text": "المحقق: يتحقق من دور شخص كل ليلة", "size": "xs", "wrap": True, "color": c["text"], "margin": "xs"},
                            {"type": "text", "text": "المواطنون: يصوتون لطرد المشتبه بهم نهارا", "size": "xs", "wrap": True, "color": c["text"], "margin": "xs"}
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
                                "backgroundColor": c["card"],
                                "cornerRadius": "12px",
                                "paddingAll": "12px",
                                "contents": [
                                    {"type": "text", "text": f"{count}/{self.max_players}", "size": "xl", "weight": "bold", "align": "center", "color": c["primary"]},
                                    {"type": "text", "text": "اللاعبون", "size": "xs", "align": "center", "color": c["text"], "margin": "xs"}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "backgroundColor": c["card"],
                                "cornerRadius": "12px",
                                "paddingAll": "12px",
                                "contents": [
                                    {"type": "text", "text": str(self.min_players), "size": "xl", "weight": "bold", "align": "center", "color": c["primary"]},
                                    {"type": "text", "text": "مطلوب", "size": "xs", "align": "center", "color": c["text"], "margin": "xs"}
                                ]
                            }
                        ]
                    }
                ] + player_list + [
                    {"type": "button", "style": "primary", "margin": "lg", "action": {"type": "message", "label": "انضمام", "text": "انضم"}, "color": c["button"], "height": "sm"},
                    {"type": "button", "style": "secondary", "margin": "sm", "action": {"type": "message", "label": "بدء اللعبة", "text": "ابدا"}, "color": c["button"], "height": "sm"},
                    {"type": "button", "style": "secondary", "margin": "sm", "action": {"type": "message", "label": "إلغاء", "text": "ايقاف"}, "color": c["button"], "height": "sm"}
                ]
            }
        }
        return FlexMessage(alt_text="مافيا", contents=FlexContainer.from_dict(bubble))

    def start_mafia_game(self):
        """بدء لعبة المافيا الفعلية"""
        if len(self.players) < self.min_players:
            return TextMessage(text=f"عدد اللاعبين غير كاف. يحتاج {self.min_players} لاعبين على الأقل")
        self._assign_roles()
        self._send_roles_privately()
        self.phase = "night"
        self.phase_start_time = time.time()
        self.round_number = 1
        for uid in self.alive_players:
            msg = self.build_night_flex(uid)
            if msg:
                try:
                    self.line_bot_api.push_message(PushMessageRequest(to=uid, messages=[msg]))
                except:
                    pass
        return TextMessage(text="بدأت اللعبة! تم إرسال الأدوار للجميع في الخاص")

    def _assign_roles(self):
        """توزيع الأدوار على اللاعبين"""
        ids = list(self.players.keys())
        random.shuffle(ids)
        mafia_count = max(1, len(ids) // 3)
        self.mafia = set(ids[:mafia_count])
        rest = ids[mafia_count:]
        self.doctor = rest[0] if len(rest) > 0 else None
        self.detective = rest[1] if len(rest) > 1 else None
        self.citizens = set(rest[2:]) if len(rest) > 2 else set()
        for uid in self.mafia:
            self.roles[uid] = "مافيا"
        if self.doctor:
            self.roles[self.doctor] = "دكتور"
        if self.detective:
            self.roles[self.detective] = "محقق"
        for uid in self.citizens:
            self.roles[uid] = "مواطن"

    def _send_roles_privately(self):
        """إرسال الأدوار للاعبين بشكل خاص"""
        for uid, role in self.roles.items():
            role_desc = {
                "مافيا": "أنت من المافيا! اختر ضحية كل ليلة",
                "دكتور": "أنت الدكتور! احم شخصا واحدا كل ليلة",
                "محقق": "أنت المحقق! تحقق من دور شخص كل ليلة",
                "مواطن": "أنت مواطن! صوت بحكمة نهارا"
            }
            try:
                self.line_bot_api.push_message(PushMessageRequest(to=uid, messages=[TextMessage(text=f"دورك: {role}\n{role_desc.get(role, '')}")]))
            except:
                pass

    def build_night_flex(self, user_id):
        """بناء رسالة الليل"""
        role = self.roles.get(user_id)
        c = self.themes[self.theme]
        if user_id not in self.alive_players:
            return None
        if role not in ["مافيا", "دكتور", "محقق"]:
            return TextMessage(text="أنت نائم الآن. انتظر النهار للتصويت")
        
        buttons = []
        for uid in self.alive_players:
            if uid == user_id:
                continue
            buttons.append({
                "type": "button",
                "style": "secondary",
                "margin": "sm",
                "action": {"type": "message", "label": self.players[uid]["name"], "text": f"اختيار {uid}"},
                "color": c["button"],
                "height": "sm"
            })
        
        role_titles = {"مافيا": "اختر ضحية", "دكتور": "اختر من تحمي", "محقق": "اختر من تحقق منه"}
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "backgroundColor": c["bg"],
                "contents": [
                    {"type": "text", "text": f"دورك: {role}", "align": "center", "size": "xl", "weight": "bold", "color": c["primary"]},
                    {"type": "text", "text": role_titles.get(role, "اختر لاعبا"), "align": "center", "size": "sm", "color": c["text"], "margin": "sm"},
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {"type": "box", "layout": "vertical", "margin": "lg", "spacing": "sm", "contents": buttons}
                ]
            }
        }
        return FlexMessage(alt_text="ليل", contents=FlexContainer.from_dict(bubble))

    def build_vote_flex(self, voter_id):
        """بناء رسالة التصويت"""
        c = self.themes[self.theme]
        buttons = []
        for uid in self.alive_players:
            if uid == voter_id:
                continue
            buttons.append({
                "type": "button",
                "style": "secondary",
                "margin": "sm",
                "action": {"type": "message", "label": self.players[uid]["name"], "text": f"تصويت {uid}"},
                "color": c["button"],
                "height": "sm"
            })
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "backgroundColor": c["bg"],
                "contents": [
                    {"type": "text", "text": "وقت التصويت", "align": "center", "size": "xl", "weight": "bold", "color": c["primary"]},
                    {"type": "text", "text": "اختر من تريد طرده", "align": "center", "size": "sm", "color": c["text"], "margin": "sm"},
                    {"type": "separator", "margin": "lg", "color": c["border"]},
                    {"type": "box", "layout": "vertical", "margin": "lg", "spacing": "sm", "contents": buttons}
                ]
            }
        }
        return FlexMessage(alt_text="تصويت", contents=FlexContainer.from_dict(bubble))

    def handle_message(self, user_id, text, display_name=None):
        """معالجة رسائل اللعبة"""
        self.check_timeout()
        if text == "انضم":
            return self.join_player(user_id, display_name)
        if text == "ابدا":
            return self.start_mafia_game()
        if text == "ايقاف":
            self.reset_game()
            return TextMessage(text="تم إيقاف اللعبة")
        if text.startswith("اختيار") and self.phase == "night":
            target = text.split()[-1]
            return self.handle_night_action(user_id, target)
        if text.startswith("تصويت") and self.phase == "day":
            target = text.split()[-1]
            return self.handle_vote(user_id, target)
        return None

    def handle_night_action(self, user_id, target):
        """معالجة أفعال الليل"""
        role = self.roles.get(user_id)
        if role not in ["مافيا", "دكتور", "محقق"]:
            return TextMessage(text="ليس دورك الآن")
        if target not in self.alive_players:
            return TextMessage(text="اللاعب المختار غير موجود")
        
        self.night_actions[role] = target
        
        if role == "محقق":
            target_role = self.roles.get(target, "غير معروف")
            try:
                self.line_bot_api.push_message(PushMessageRequest(to=user_id, messages=[TextMessage(text=f"دور {self.players[target]['name']}: {target_role}")]))
            except:
                pass
        
        if self._night_complete():
            return self._resolve_night()
        return TextMessage(text="تم تسجيل اختيارك. في انتظار باقي اللاعبين...")

    def _night_complete(self):
        """التحقق من اكتمال أفعال الليل"""
        required = []
        if any(m in self.alive_players for m in self.mafia):
            required.append("مافيا")
        if self.doctor and self.doctor in self.alive_players:
            required.append("دكتور")
        if self.detective and self.detective in self.alive_players:
            required.append("محقق")
        return all(r in self.night_actions for r in required)

    def _resolve_night(self):
        """حل أفعال الليل"""
        kill = self.night_actions.get("مافيا")
        save = self.night_actions.get("دكتور")
        killed_name = None
        
        if kill and kill != save and kill in self.alive_players:
            killed_name = self.players[kill]["name"]
            self.alive_players.remove(kill)
            self.players[kill]["alive"] = False
            self.dead_players.add(kill)
        
        self.night_actions = {}
        
        if self._check_end():
            return self._build_end_message()
        
        self.phase = "day"
        self.phase_start_time = time.time()
        
        for uid in self.alive_players:
            try:
                self.line_bot_api.push_message(PushMessageRequest(to=uid, messages=[self.build_vote_flex(uid)]))
            except:
                pass
        
        if killed_name:
            return TextMessage(text=f"انتهى الليل. {killed_name} قتل!")
        return TextMessage(text="انتهى الليل. لم يقتل أحد!")

    def handle_vote(self, voter, target):
        """معالجة التصويت"""
        if voter not in self.alive_players:
            return TextMessage(text="أنت خارج اللعبة")
        if target not in self.alive_players:
            return TextMessage(text="اللاعب المختار غير موجود")
        
        self.votes[voter] = target
        
        if len(self.votes) == len(self.alive_players):
            return self._resolve_votes()
        return TextMessage(text=f"تم تسجيل تصويتك. ({len(self.votes)}/{len(self.alive_players)})")

    def _resolve_votes(self):
        """حل التصويت"""
        if not self.votes:
            self.phase = "night"
            self.phase_start_time = time.time()
            self.round_number += 1
            return TextMessage(text="لم يصوت أحد. بدأت ليلة جديدة")
        
        counts = Counter(self.votes.values())
        eliminated, vote_count = counts.most_common(1)[0]
        eliminated_name = self.players[eliminated]["name"]
        eliminated_role = self.roles[eliminated]
        
        self.alive_players.remove(eliminated)
        self.players[eliminated]["alive"] = False
        self.dead_players.add(eliminated)
        self.votes = {}
        
        if self._check_end():
            return self._build_end_message()
        
        self.phase = "night"
        self.phase_start_time = time.time()
        self.round_number += 1
        
        for uid in self.alive_players:
            try:
                self.line_bot_api.push_message(PushMessageRequest(to=uid, messages=[self.build_night_flex(uid)]))
            except:
                pass
        
        return TextMessage(text=f"تم طرد {eliminated_name} ({eliminated_role}) بـ {vote_count} صوت. بدأت ليلة جديدة")

    def _check_end(self):
        """التحقق من نهاية اللعبة"""
        mafia_alive = [m for m in self.mafia if m in self.alive_players]
        citizens_alive = len(self.alive_players) - len(mafia_alive)
        return len(mafia_alive) == 0 or len(mafia_alive) >= citizens_alive

    def _build_end_message(self):
        """بناء رسالة النهاية"""
        mafia_alive = [m for m in self.mafia if m in self.alive_players]
        if len(mafia_alive) == 0:
            winner = "المواطنون"
        else:
            winner = "المافيا"
        
        mafia_names = [self.players[m]["name"] for m in self.mafia]
        result_text = f"انتهت اللعبة!\n\nالفائز: {winner}\n\nالمافيا كانوا:\n" + "\n".join([f"- {name}" for name in mafia_names])
        
        self.reset_game()
        return TextMessage(text=result_text)

    def check_timeout(self):
        """التحقق من انتهاء الوقت"""
        if not self.phase_start_time:
            return
        elapsed = time.time() - self.phase_start_time
        
        if self.phase == "night" and elapsed >= self.night_timeout:
            self._resolve_night()
        elif self.phase == "day" and elapsed >= self.vote_timeout:
            if self.votes:
                self._resolve_votes()
            else:
                self.phase = "night"
                self.phase_start_time = time.time()
                self.round_number += 1
    
    def check_answer(self, user_answer, user_id, display_name):
        """متطلب من BaseGame"""
        return self.handle_message(user_id, user_answer, display_name)
