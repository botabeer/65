from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
import threading

# =========================
# Models
# =========================

@dataclass
class Player:
    user_id: str
    display_name: str
    score: int = 0
    joined_at: datetime = field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None
    is_active: bool = True
    game_data: Dict[str, Any] = field(default_factory=dict)

    def touch(self):
        self.last_activity = datetime.now()


@dataclass
class GameSession:
    group_id: str
    game_name: str
    players: Dict[str, Player] = field(default_factory=dict)
    game_state: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def touch(self):
        self.updated_at = datetime.now()


@dataclass
class UserActivity:
    user_id: str
    message_count: int = 0
    last_reset: datetime = field(default_factory=datetime.now)
    warnings: int = 0
    ban_until: Optional[datetime] = None


# =========================
# Database
# =========================

class Database:
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}
        self.user_activities: Dict[str, UserActivity] = {}
        self.admins: Set[str] = set()
        self.banned_users: Dict[str, datetime] = {}
        self.lock = threading.RLock()

    # -------- Sessions --------

    def create_session(self, group_id: str, game_name: str) -> Optional[GameSession]:
        with self.lock:
            if group_id in self.sessions:
                return None
            session = GameSession(group_id=group_id, game_name=game_name)
            self.sessions[group_id] = session
            return session

    def get_session(self, group_id: str) -> Optional[GameSession]:
        return self.sessions.get(group_id)

    def end_session(self, group_id: str) -> bool:
        with self.lock:
            session = self.sessions.get(group_id)
            if not session:
                return False
            session.is_active = False
            session.touch()
            return True

    def delete_session(self, group_id: str):
        with self.lock:
            self.sessions.pop(group_id, None)

    # -------- Players --------

    def add_player(self, group_id: str, user_id: str, display_name: str) -> bool:
        with self.lock:
            session = self.get_session(group_id)
            if not session or not session.is_active:
                return False
            if user_id in session.players:
                return False

            player = Player(user_id=user_id, display_name=display_name)
            player.touch()
            session.players[user_id] = player
            session.touch()
            return True

    def remove_player(self, group_id: str, user_id: str) -> bool:
        with self.lock:
            session = self.get_session(group_id)
            if not session or user_id not in session.players:
                return False
            del session.players[user_id]
            session.touch()
            return True

    def is_player_registered(self, group_id: str, user_id: str) -> bool:
        session = self.get_session(group_id)
        return bool(session and user_id in session.players)

    def get_player(self, group_id: str, user_id: str) -> Optional[Player]:
        session = self.get_session(group_id)
        return session.players.get(user_id) if session else None

    def update_player_score(self, group_id: str, user_id: str, points: int):
        with self.lock:
            player = self.get_player(group_id, user_id)
            if not player:
                return
            player.score += points
            player.touch()
            self.sessions[group_id].touch()

    # -------- Game State --------

    def update_game_state(self, group_id: str, key: str, value: Any):
        with self.lock:
            session = self.get_session(group_id)
            if not session:
                return
            session.game_state[key] = value
            session.touch()

    def get_game_state(self, group_id: str, key: str, default: Any = None) -> Any:
        session = self.get_session(group_id)
        return session.game_state.get(key, default) if session else default

    # -------- Leaderboard --------

    def get_leaderboard(self, group_id: str, limit: int = 10) -> List[Player]:
        session = self.get_session(group_id)
        if not session:
            return []
        return sorted(
            session.players.values(),
            key=lambda p: p.score,
            reverse=True
        )[:limit]

    # -------- Anti Spam --------

    def record_message(self, user_id: str, limit_seconds: int = 60) -> int:
        with self.lock:
            now = datetime.now()
            activity = self.user_activities.setdefault(
                user_id, UserActivity(user_id=user_id)
            )

            if (now - activity.last_reset).total_seconds() > limit_seconds:
                activity.message_count = 0
                activity.last_reset = now

            activity.message_count += 1
            return activity.message_count

    def is_rate_limited(self, user_id: str, limit: int = 5) -> bool:
        return self.record_message(user_id) > limit

    # -------- Warnings / Ban --------

    def add_warning(self, user_id: str) -> int:
        with self.lock:
            activity = self.user_activities.setdefault(
                user_id, UserActivity(user_id=user_id)
            )
            activity.warnings += 1
            return activity.warnings

    def ban_user(self, user_id: str, duration: timedelta):
        with self.lock:
            until = datetime.now() + duration
            self.banned_users[user_id] = until
            activity = self.user_activities.setdefault(
                user_id, UserActivity(user_id=user_id)
            )
            activity.ban_until = until

    def unban_user(self, user_id: str):
        with self.lock:
            self.banned_users.pop(user_id, None)
            if user_id in self.user_activities:
                self.user_activities[user_id].ban_until = None
                self.user_activities[user_id].warnings = 0

    def is_banned(self, user_id: str) -> bool:
        until = self.banned_users.get(user_id)
        if not until:
            return False
        if datetime.now() > until:
            self.unban_user(user_id)
            return False
        return True

    def can_interact(self, user_id: str) -> bool:
        return not self.is_banned(user_id)

    # -------- Admins --------

    def add_admin(self, user_id: str):
        with self.lock:
            self.admins.add(user_id)

    def remove_admin(self, user_id: str):
        with self.lock:
            self.admins.discard(user_id)

    def is_admin(self, user_id: str) -> bool:
        return user_id in self.admins

    # -------- Cleanup --------

    def cleanup_old_sessions(self, hours: int = 24) -> int:
        with self.lock:
            now = datetime.now()
            expired = [
                gid for gid, s in self.sessions.items()
                if (now - s.updated_at).total_seconds() > hours * 3600
            ]
            for gid in expired:
                del self.sessions[gid]
            return len(expired)


db = Database()
