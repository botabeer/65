import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_loader import BaseGame
from config import Config
import random

class MafiaGame(BaseGame):
    def __init__(self):
        super().__init__()
        self.name = "لعبة المافيا"
        self.description = "لعبة اجتماعية - مافيا ضد مواطنين"
        self.min_players = 4
        self.max_players = 15
    
    def start(self, group_id: str, players: dict) -> tuple[bool, str]:
        from database import db
        
        player_count = len(players)
        
        num_mafia = max(1, player_count // 4)
        num_detective = 1 if player_count >= 6 else 0
        num_doctor = 1 if player_count >= 8 else 0
        
        roles_list = ["مافيا"] * num_mafia
        if num_detective:
            roles_list.append("محقق")
        if num_doctor:
            roles_list.append("طبيب")
        
        while len(roles_list) < player_count:
            roles_list.append("مواطن")
        
        random.shuffle(roles_list)
        
        player_ids = list(players.keys())
        random.shuffle(player_ids)
        
        roles = {}
        for i, player_id in enumerate(player_ids):
            roles[player_id] = roles_list[i]
        
        db.update_game_state(group_id, 'roles', roles)
        db.update_game_state(group_id, 'alive', player_ids.copy())
        db.update_game_state(group_id, 'phase', 'night')
        db.update_game_state(group_id, 'day_count', 1)
        db.update_game_state(group_id, 'votes', {})
        db.update_game_state(group_id, 'night_actions', {})
        
        message = f"بدأت لعبة المافيا\n\n"
        message += f"عدد اللاعبين: {player_count}\n"
        message += f"المافيا: {num_mafia}\n"
        if num_detective:
            message += f"المحقق: 1\n"
        if num_doctor:
            message += f"الطبيب: 1\n"
        message += f"المواطنون: {player_count - num_mafia - num_detective - num_doctor}\n\n"
        message += "الليل الأول\n"
        message += "المافيا: اختاروا ضحيتكم\n"
        if num_detective:
            message += "المحقق: اختر لاعب للفحص\n"
        if num_doctor:
            message += "الطبيب: اختر لاعب للحماية\n\n"
        message += "ملاحظة: الأدوار سرية - سيتم إرسال رسالة خاصة لكل لاعب بدوره"
        
        return True, message
    
    def process_message(self, group_id: str, user_id: str, message: str) -> tuple[str, bool]:
        from database import db
        
        roles = db.get_game_state(group_id, 'roles', {})
        alive = db.get_game_state(group_id, 'alive', [])
        phase = db.get_game_state(group_id, 'phase', 'night')
        votes = db.get_game_state(group_id, 'votes', {})
        night_actions = db.get_game_state(group_id, 'night_actions', {})
        
        if user_id not in alive:
            return None, False
        
        normalized = Config.normalize(message)
        
        if normalized == 'تصويت':
            if phase != 'day':
                return "التصويت متاح في النهار فقط", True
            return self._show_vote_options(group_id), True
        
        if normalized.startswith('صوت'):
            if phase != 'day':
                return "التصويت متاح في النهار فقط", True
            return self._process_vote(group_id, user_id, message), True
        
        if phase == 'night':
            role = roles.get(user_id)
            if role in ['مافيا', 'محقق', 'طبيب']:
                return self._process_night_action(group_id, user_id, role, message), True
        
        return None, False
    
    def _process_night_action(self, group_id, user_id, role, target_name):
        from database import db
        
        alive = db.get_game_state(group_id, 'alive', [])
        players = db.get_session(group_id).players
        night_actions = db.get_game_state(group_id, 'night_actions', {})
        
        target_id = None
        for pid, player in players.items():
            if Config.normalize(player.display_name) == Config.normalize(target_name):
                target_id = pid
                break
        
        if not target_id or target_id not in alive:
            return "اللاعب غير موجود أو متوفى"
        
        if target_id == user_id and role != 'طبيب':
            return "لا يمكنك اختيار نفسك"
        
        night_actions[user_id] = {'role': role, 'target': target_id}
        db.update_game_state(group_id, 'night_actions', night_actions)
        
        roles = db.get_game_state(group_id, 'roles', {})
        mafia_count = sum(1 for uid in alive if roles.get(uid) == 'مافيا')
        special_roles = ['محقق', 'طبيب']
        special_count = sum(1 for uid in alive if roles.get(uid) in special_roles)
        
        required_actions = mafia_count + special_count
        current_actions = len(night_actions)
        
        if current_actions >= required_actions:
            return self._process_night_end(group_id)
        
        return f"تم تسجيل اختيارك\nالانتظار: {current_actions}/{required_actions}"
    
    def _process_night_end(self, group_id):
        from database import db
        
        night_actions = db.get_game_state(group_id, 'night_actions', {})
        alive = db.get_game_state(group_id, 'alive', [])
        roles = db.get_game_state(group_id, 'roles', {})
        day_count = db.get_game_state(group_id, 'day_count', 1)
        
        mafia_target = None
        doctor_target = None
        detective_result = None
        
        for user_id, action in night_actions.items():
            if action['role'] == 'مافيا' and not mafia_target:
                mafia_target = action['target']
            elif action['role'] == 'طبيب':
                doctor_target = action['target']
            elif action['role'] == 'محقق':
                target = action['target']
                target_role = roles.get(target, 'مواطن')
                detective_result = f"اللاعب مافيا" if target_role == 'مافيا' else "اللاعب بريء"
        
        message = f"انتهى الليل {day_count}\n\n"
        
        if mafia_target and mafia_target != doctor_target:
            alive.remove(mafia_target)
            player_name = db.get_session(group_id).players[mafia_target].display_name
            message += f"تم قتل {player_name}\n"
        else:
            message += "الطبيب نجح في إنقاذ الضحية\n"
        
        db.update_game_state(group_id, 'alive', alive)
        db.update_game_state(group_id, 'phase', 'day')
        db.update_game_state(group_id, 'votes', {})
        db.update_game_state(group_id, 'night_actions', {})
        
        winner = self._check_win(group_id)
        if winner:
            return self._end_game(group_id, winner)
        
        message += f"\nالنهار {day_count}\n"
        message += "ناقشوا واختاروا من تريدون تصفيته\n"
        message += "استخدم: صوت [اسم اللاعب]"
        
        return message
    
    def _process_vote(self, group_id, user_id, message):
        from database import db
        
        votes = db.get_game_state(group_id, 'votes', {})
        alive = db.get_game_state(group_id, 'alive', [])
        players = db.get_session(group_id).players
        
        target_name = message.replace('صوت', '').strip()
        target_id = None
        
        for pid, player in players.items():
            if Config.normalize(player.display_name) == Config.normalize(target_name):
                target_id = pid
                break
        
        if not target_id or target_id not in alive:
            return "اللاعب غير موجود أو متوفى"
        
        votes[user_id] = target_id
        db.update_game_state(group_id, 'votes', votes)
        
        if len(votes) >= len(alive):
            return self._process_day_end(group_id)
        
        return f"تم تسجيل صوتك\nالأصوات: {len(votes)}/{len(alive)}"
    
    def _process_day_end(self, group_id):
        from database import db
        
        votes = db.get_game_state(group_id, 'votes', {})
        alive = db.get_game_state(group_id, 'alive', [])
        day_count = db.get_game_state(group_id, 'day_count', 1)
        
        vote_count = {}
        for target in votes.values():
            vote_count[target] = vote_count.get(target, 0) + 1
        
        if vote_count:
            executed = max(vote_count, key=vote_count.get)
            alive.remove(executed)
            player_name = db.get_session(group_id).players[executed].display_name
            
            message = f"تم تصفية {player_name} بالتصويت\n"
        else:
            message = "لم يتم تصفية أحد\n"
        
        db.update_game_state(group_id, 'alive', alive)
        db.update_game_state(group_id, 'phase', 'night')
        db.update_game_state(group_id, 'day_count', day_count + 1)
        db.update_game_state(group_id, 'votes', {})
        db.update_game_state(group_id, 'night_actions', {})
        
        winner = self._check_win(group_id)
        if winner:
            return self._end_game(group_id, winner)
        
        message += f"\nالليل {day_count + 1}\n"
        message += "المافيا: اختاروا ضحيتكم"
        
        return message
    
    def _check_win(self, group_id):
        from database import db
        
        roles = db.get_game_state(group_id, 'roles', {})
        alive = db.get_game_state(group_id, 'alive', [])
        
        mafia_alive = sum(1 for uid in alive if roles.get(uid) == 'مافيا')
        citizen_alive = len(alive) - mafia_alive
        
        if mafia_alive == 0:
            return 'citizens'
        elif mafia_alive >= citizen_alive:
            return 'mafia'
        
        return None
    
    def _end_game(self, group_id, winner):
        from database import db
        
        roles = db.get_game_state(group_id, 'roles', {})
        players = db.get_session(group_id).players
        
        message = "انتهت اللعبة\n\n"
        
        if winner == 'mafia':
            message += "فازت المافيا\n\n"
            points = 3
        else:
            message += "فاز المواطنون\n\n"
            points = 2
        
        message += "الأدوار:\n"
        for user_id, role in roles.items():
            player_name = players[user_id].display_name
            message += f"{player_name}: {role}\n"
            
            if (winner == 'mafia' and role == 'مافيا') or (winner == 'citizens' and role != 'مافيا'):
                db.update_player_score(group_id, user_id, points)
        
        return message
    
    def _show_vote_options(self, group_id):
        from database import db
        
        alive = db.get_game_state(group_id, 'alive', [])
        players = db.get_session(group_id).players
        
        message = "اللاعبون الأحياء:\n"
        for uid in alive:
            message += f"- {players[uid].display_name}\n"
        
        message += "\nاستخدم: صوت [اسم اللاعب]"
        
        return message
    
    def end(self, group_id: str) -> tuple[bool, str]:
        from database import db
        
        roles = db.get_game_state(group_id, 'roles', {})
        players = db.get_session(group_id).players
        
        message = "تم إيقاف اللعبة\n\nالأدوار:\n"
        for user_id, role in roles.items():
            player_name = players[user_id].display_name
            message += f"{player_name}: {role}\n"
        
        return True, message
    
    def get_status(self, group_id: str) -> str:
        from database import db
        
        alive = db.get_game_state(group_id, 'alive', [])
        phase = db.get_game_state(group_id, 'phase', 'night')
        day_count = db.get_game_state(group_id, 'day_count', 1)
        players = db.get_session(group_id).players
        
        phase_name = "الليل" if phase == 'night' else "النهار"
        
        message = f"المرحلة: {phase_name} {day_count}\n\n"
        message += "اللاعبون الأحياء:\n"
        
        for uid in alive:
            player_name = players[uid].display_name
            message += f"- {player_name}\n"
        
        return message
