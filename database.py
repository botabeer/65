from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
import threading

@dataclass
class Player:
    user_id: str
    display_name: str
    score: int = 0
    joined_at: datetime = field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None
    is_active: bool = True
    game_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GameSession:
    group_id: str
    game_name: str
    players: Dict[str, Player] = field(default_factory=dict)
    game_state: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class UserActivity:
    user_id: str
    message_count: int = 0
    last_reset: datetime = field(default_factory=datetime.now)
    warnings: int = 0
    ban_until: Optional[datetime] = None

class Database:
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}
        self.user_activities: Dict[str, UserActivity] = {}
        self.admins: Set[str] = set()
        self.banned_users: Dict[str, datetime] = {}
        self.lock = threading.Lock()
    
    def create_session(self, group_id: str, game_name: str) -> GameSession:
        with self.lock:
            self.sessions[group_id] = GameSession(group_id=group_id, game_name=game_name)
            return self.sessions[group_id]
    
    def get_session(self, group_id: str) -> Optional[GameSession]:
        return self.sessions.get(group_id)
    
    def delete_session(self, group_id: str):
        with self.lock:
            if group_id in self.sessions:
                del self.sessions[group_id]
    
    def add_player(self, group_id: str, user_id: str, display_name: str) -> bool:
        with self.lock:
            session = self.get_session(group_id)
            if not session:
                return False
            
            if user_id in session.players:
                return False
            
            session.players[user_id] = Player(user_id=user_id, display_name=display_name)
            session.updated_at = datetime.now()
            return True
    
    def remove_player(self, group_id: str, user_id: str) -> bool:
        with self.lock:
            session = self.get_session(group_id)
            if not session or user_id not in session.players:
                return False
            
            del session.players[user_id]
            session.updated_at = datetime.now()
            return True
    
    def is_player_registered(self, group_id: str, user_id: str) -> bool:
        session = self.get_session(group_id)
        return session and user_id in session.players
    
    def get_player(self, group_id: str, user_id: str) -> Optional[Player]:
        session = self.get_session(group_id)
        if session:
            return session.players.get(user_id)
        return None
    
    def update_player_score(self, group_id: str, user_id: str, points: int):
        with self.lock:
            session = self.get_session(group_id)
            if session and user_id in session.players:
                session.players[user_id].score += points
                session.updated_at = datetime.now()
    
    def update_game_state(self, group_id: str, key: str, value: Any):
        with self.lock:
            session = self.get_session(group_id)
            if session:
                session.game_state[key] = value
                session.updated_at = datetime.now()
    
    def get_game_state(self, group_id: str, key: str, default: Any = None) -> Any:
        session = self.get_session(group_id)
        if session:
            return session.game_state.get(key, default)
        return default
    
    def get_leaderboard(self, group_id: str) -> List[Player]:
        session = self.get_session(group_id)
        if not session:
            return []
        return sorted(session.players.values(), key=lambda p: p.score, reverse=True)
    
    def record_message(self, user_id: str) -> int:
        with self.lock:
            now = datetime.now()
            
            if user_id not in self.user_activities:
                self.user_activities[user_id] = UserActivity(user_id=user_id)
            
            activity = self.user_activities[user_id]
            
            if (now - activity.last_reset).total_seconds() > 60:
                activity.message_count = 0
                activity.last_reset = now
            
            activity.message_count += 1
            return activity.message_count
    
    def add_warning(self, user_id: str) -> int:
        with self.lock:
            if user_id not in self.user_activities:
                self.user_activities[user_id] = UserActivity(user_id=user_id)
            
            self.user_activities[user_id].warnings += 1
            return self.user_activities[user_id].warnings
    
    def ban_user(self, user_id: str, duration: timedelta):
        with self.lock:
            self.banned_users[user_id] = datetime.now() + duration
            if user_id in self.user_activities:
                self.user_activities[user_id].ban_until = self.banned_users[user_id]
    
    def unban_user(self, user_id: str):
        with self.lock:
            if user_id in self.banned_users:
                del self.banned_users[user_id]
            if user_id in self.user_activities:
                self.user_activities[user_id].ban_until = None
                self.user_activities[user_id].warnings = 0
    
    def is_banned(self, user_id: str) -> bool:
        if user_id not in self.banned_users:
            return False
        
        if datetime.now() > self.banned_users[user_id]:
            self.unban_user(user_id)
            return False
        
        return True
    
    def add_admin(self, user_id: str):
        with self.lock:
            self.admins.add(user_id)
    
    def remove_admin(self, user_id: str):
        with self.lock:
            self.admins.discard(user_id)
    
    def is_admin(self, user_id: str) -> bool:
        return user_id in self.admins
    
    def cleanup_old_sessions(self, hours: int = 24):
        with self.lock:
            now = datetime.now()
            to_delete = []
            
            for group_id, session in self.sessions.items():
                if (now - session.updated_at).total_seconds() > hours * 3600:
                    to_delete.append(group_id)
            
            for group_id in to_delete:
                del self.sessions[group_id]
            
            return len(to_delete)

db = Database()
