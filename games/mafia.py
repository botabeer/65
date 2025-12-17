import random
from games.base import BaseGame
from config import Config

class MafiaGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة المافيا"
        self.supports_hint = False
        self.supports_reveal = False
        self.min_players = 4
        self.max_players = 12
        self.players = []
        self.roles = {}
        self.alive_players = []
        self.phase = "setup"
        self.day_count = 0
        self.votes = {}
    
    def get_question(self):
        if self.phase == "setup":
            question = f"لعبة المافيا - لعبة جماعية\n\nعدد اللاعبين: {self.min_players}-{self.max_players}\n\nالأدوار:\n• مافيا - يقتل ليلا\n• محقق - يفحص ليلا\n• طبيب - يحمي ليلا\n• مواطن - يصوت نهارا\n\nلبدء اللعبة يجب:\n1. جمع {self.min_players} لاعبين على الأقل\n2. كل لاعب يكتب 'انضم'\n3. عند اكتمال العدد اكتب 'ابدأ'\n\nحالة اللعبة: قيد التطوير\nهذه النسخة تجريبية"
            return self.build_question_flex(question, None)
        
        return self.build_question_flex("قيد التطوير", None)
    
    def check_answer(self, answer: str) -> bool:
        return False
    
    def _assign_roles(self):
        num_players = len(self.players)
        num_mafia = max(1, num_players // 4)
        num_detective = 1 if num_players >= 6 else 0
        num_doctor = 1 if num_players >= 8 else 0
        
        roles_list = ["مافيا"] * num_mafia
        if num_detective:
            roles_list.append("محقق")
        if num_doctor:
            roles_list.append("طبيب")
        
        while len(roles_list) < num_players:
            roles_list.append("مواطن")
        
        random.shuffle(roles_list)
        
        for i, player in enumerate(self.players):
            self.roles[player] = roles_list[i]
        
        self.alive_players = self.players.copy()
    
    def _check_win_condition(self):
        mafia_alive = sum(1 for p in self.alive_players if self.roles[p] == "مافيا")
        citizen_alive = len(self.alive_players) - mafia_alive
        
        if mafia_alive == 0:
            return "citizens"
        elif mafia_alive >= citizen_alive:
            return "mafia"
        return None
