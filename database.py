import sqlite3
import logging
import time
from datetime import datetime, timedelta
from contextlib import contextmanager
from threading import Lock
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DB_PATH
        self._lock = Lock()
        self._waiting_names = {}
        self._changing_names = {}
        self._game_progress = {}
        self._unregistered = set()
        self._init_db()
    
    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    points INTEGER DEFAULT 0,
                    games INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    theme TEXT DEFAULT 'light',
                    last_active TIMESTAMP,
                    created_at TIMESTAMP,
                    last_reward TIMESTAMP,
                    streak INTEGER DEFAULT 0,
                    best_streak INTEGER DEFAULT 0,
                    games_played TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    user_id TEXT,
                    achievement_id TEXT,
                    unlocked_at TIMESTAMP,
                    PRIMARY KEY (user_id, achievement_id)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_points ON users(points DESC, wins DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_active ON users(last_active DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_streak ON users(streak DESC)")
    
    def is_registered(self, user_id):
        with self._lock:
            if user_id in self._unregistered:
                return False
        with self._get_conn() as conn:
            row = conn.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,)).fetchone()
            return row is not None
    
    def register_user(self, user_id, name):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO users (user_id, name, last_active, created_at, last_reward)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, name, now, now, now))
        with self._lock:
            self._unregistered.discard(user_id)
    
    def get_user(self, user_id):
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
            return dict(row) if row else None
    
    def update_activity(self, user_id):
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            conn.execute("UPDATE users SET last_active=? WHERE user_id=?", (now, user_id))
    
    def update_name(self, user_id, name):
        with self._get_conn() as conn:
            conn.execute("UPDATE users SET name=? WHERE user_id=?", (name, user_id))
    
    def change_theme(self, user_id, theme):
        with self._get_conn() as conn:
            conn.execute("UPDATE users SET theme=? WHERE user_id=?", (theme, user_id))
    
    def add_points(self, user_id, points):
        with self._get_conn() as conn:
            conn.execute("UPDATE users SET points=points+? WHERE user_id=?", (points, user_id))
    
    def increment_games(self, user_id):
        with self._get_conn() as conn:
            conn.execute("UPDATE users SET games=games+1 WHERE user_id=?", (user_id,))
    
    def increment_wins(self, user_id):
        with self._get_conn() as conn:
            conn.execute("UPDATE users SET wins=wins+1, streak=streak+1 WHERE user_id=?", (user_id,))
            user = self.get_user(user_id)
            if user and user['streak'] > user['best_streak']:
                conn.execute("UPDATE users SET best_streak=streak WHERE user_id=?", (user_id,))
    
    def reset_streak(self, user_id):
        with self._get_conn() as conn:
            conn.execute("UPDATE users SET streak=0 WHERE user_id=?", (user_id,))
    
    def add_game_played(self, user_id, game_name):
        user = self.get_user(user_id)
        if user:
            played = user.get('games_played', '').split(',')
            if game_name not in played:
                played.append(game_name)
                played_str = ','.join(filter(None, played))
                with self._get_conn() as conn:
                    conn.execute("UPDATE users SET games_played=? WHERE user_id=?", (played_str, user_id))
    
    def get_leaderboard(self, limit=10):
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT name, points, wins, games, streak, best_streak
                FROM users ORDER BY points DESC, wins DESC LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]
    
    def unregister(self, user_id):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            conn.execute("DELETE FROM achievements WHERE user_id=?", (user_id,))
        with self._lock:
            self._unregistered.add(user_id)
            self._waiting_names.pop(user_id, None)
            self._changing_names.pop(user_id, None)
            self._game_progress.pop(user_id, None)
    
    def can_claim_reward(self, user_id):
        user = self.get_user(user_id)
        if not user or not user.get('last_reward'):
            return True
        last = datetime.fromisoformat(user['last_reward'])
        return datetime.now() - last >= timedelta(hours=Config.DAILY_REWARD_HOURS)
    
    def claim_reward(self, user_id):
        if self.can_claim_reward(user_id):
            now = datetime.now().isoformat()
            with self._get_conn() as conn:
                conn.execute("UPDATE users SET points=points+?, last_reward=? WHERE user_id=?",
                           (Config.DAILY_REWARD_POINTS, now, user_id))
            return True
        return False
    
    def unlock_achievement(self, user_id, achievement_id):
        with self._get_conn() as conn:
            existing = conn.execute("SELECT 1 FROM achievements WHERE user_id=? AND achievement_id=?",
                                   (user_id, achievement_id)).fetchone()
            if not existing:
                now = datetime.now().isoformat()
                conn.execute("INSERT INTO achievements VALUES (?, ?, ?)",
                           (user_id, achievement_id, now))
                return True
        return False
    
    def get_user_achievements(self, user_id):
        with self._get_conn() as conn:
            rows = conn.execute("SELECT achievement_id FROM achievements WHERE user_id=?",
                              (user_id,)).fetchall()
            return [row[0] for row in rows]
    
    def check_achievements(self, user_id):
        user = self.get_user(user_id)
        if not user:
            return []
        
        unlocked = self.get_user_achievements(user_id)
        new_achievements = []
        
        checks = [
            ("first_game", user['games'] >= 1),
            ("ten_games", user['games'] >= 10),
            ("fifty_games", user['games'] >= 50),
            ("hundred_games", user['games'] >= 100),
            ("first_win", user['wins'] >= 1),
            ("ten_wins", user['wins'] >= 10),
            ("hundred_points", user['points'] >= 100),
            ("streak_3", user['streak'] >= 3),
            ("streak_5", user['streak'] >= 5),
            ("all_games", len(user.get('games_played', '').split(',')) >= 12)
        ]
        
        for achievement_id, condition in checks:
            if condition and achievement_id not in unlocked:
                if self.unlock_achievement(user_id, achievement_id):
                    achievement = Config.ACHIEVEMENTS[achievement_id]
                    self.add_points(user_id, achievement['points'])
                    new_achievements.append(achievement)
        
        return new_achievements
    
    def set_waiting_name(self, user_id):
        with self._lock:
            self._waiting_names[user_id] = time.time()
    
    def is_waiting_name(self, user_id):
        with self._lock:
            return user_id in self._waiting_names
    
    def clear_waiting_name(self, user_id):
        with self._lock:
            self._waiting_names.pop(user_id, None)
    
    def set_changing_name(self, user_id):
        with self._lock:
            self._changing_names[user_id] = time.time()
    
    def is_changing_name(self, user_id):
        with self._lock:
            return user_id in self._changing_names
    
    def clear_changing_name(self, user_id):
        with self._lock:
            self._changing_names.pop(user_id, None)
    
    def set_game_progress(self, user_id, game_obj):
        with self._lock:
            self._game_progress[user_id] = game_obj
    
    def get_game_progress(self, user_id):
        with self._lock:
            return self._game_progress.get(user_id)
    
    def clear_game_progress(self, user_id):
        with self._lock:
            self._game_progress.pop(user_id, None)
    
    def has_active_game(self, user_id):
        with self._lock:
            return user_id in self._game_progress
    
    def cleanup_memory(self, timeout=1800):
        now = time.time()
        with self._lock:
            self._waiting_names = {k: v for k, v in self._waiting_names.items() if now - v < timeout}
            self._changing_names = {k: v for k, v in self._changing_names.items() if now - v < timeout}
