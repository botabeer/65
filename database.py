import sqlite3
import logging
import os
from threading import Lock
from datetime import datetime, timedelta
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "bot65.db")

class DB:
    _lock = Lock()
    _connection_pool = []
    _pool_size = 5

    @staticmethod
    @contextmanager
    def conn():
        os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else '.', exist_ok=True)
        
        c = None
        with DB._lock:
            if DB._connection_pool:
                c = DB._connection_pool.pop()
        
        if c is None:
            c = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
            c.row_factory = sqlite3.Row
            c.execute('PRAGMA journal_mode=WAL')
            c.execute('PRAGMA synchronous=NORMAL')
            c.execute('PRAGMA cache_size=10000')
        
        try:
            yield c
            c.commit()
            with DB._lock:
                if len(DB._connection_pool) < DB._pool_size:
                    DB._connection_pool.append(c)
                else:
                    c.close()
        except Exception as e:
            c.rollback()
            logger.error(f"Database error: {e}")
            c.close()
            raise

    @staticmethod
    def init():
        try:
            with DB.conn() as c:
                c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    points INTEGER DEFAULT 0,
                    games INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    theme TEXT DEFAULT 'light',
                    activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

                c.execute('''CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    game TEXT,
                    points INTEGER,
                    won INTEGER,
                    played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )''')

                c.execute('CREATE INDEX IF NOT EXISTS idx_points ON users(points DESC)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_activity ON users(activity DESC)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_history_user ON history(user_id)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_history_game ON history(game)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_history_played ON history(played DESC)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_user_game ON history(user_id, game)')
                
                c.execute('PRAGMA foreign_keys = ON')

            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @staticmethod
    def get_user(user_id):
        try:
            with DB.conn() as c:
                row = c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    @staticmethod
    def register_user(user_id, name):
        try:
            with DB.conn() as c:
                c.execute('''INSERT INTO users (user_id, name) VALUES (?, ?)
                            ON CONFLICT(user_id) DO UPDATE SET 
                            name = excluded.name, 
                            activity = CURRENT_TIMESTAMP''',
                         (user_id, name))
            logger.info(f"User registered: {user_id} - {name}")
            return True
        except Exception as e:
            logger.error(f"Error registering user {user_id}: {e}")
            return False
    
    @staticmethod
    def update_activity(user_id):
        try:
            with DB.conn() as c:
                c.execute('UPDATE users SET activity = CURRENT_TIMESTAMP WHERE user_id = ?', 
                         (user_id,))
        except Exception as e:
            logger.error(f"Error updating activity for {user_id}: {e}")
    
    @staticmethod
    def add_points(user_id, points, won, game_name):
        try:
            with DB.conn() as c:
                c.execute('''UPDATE users SET 
                            points = points + ?,
                            games = games + 1,
                            wins = wins + ?,
                            activity = CURRENT_TIMESTAMP
                            WHERE user_id = ?''', 
                         (points, 1 if won else 0, user_id))
                
                c.execute('''INSERT INTO history (user_id, game, points, won) 
                            VALUES (?, ?, ?, ?)''',
                         (user_id, game_name, points, 1 if won else 0))
            
            logger.info(f"Points added for {user_id}: {points} ({game_name})")
            return True
        except Exception as e:
            logger.error(f"Error adding points for {user_id}: {e}")
            return False
    
    @staticmethod
    def get_leaderboard(limit=20):
        try:
            with DB.conn() as c:
                rows = c.execute('''SELECT user_id, name, points, games, wins 
                                   FROM users 
                                   WHERE points > 0
                                   ORDER BY points DESC, wins DESC 
                                   LIMIT ?''', 
                                (limit,)).fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    @staticmethod
    def set_theme(user_id, theme):
        try:
            with DB.conn() as c:
                c.execute('''UPDATE users SET theme = ?, activity = CURRENT_TIMESTAMP 
                            WHERE user_id = ?''', 
                         (theme, user_id))
            logger.info(f"Theme updated for {user_id}: {theme}")
            return True
        except Exception as e:
            logger.error(f"Error setting theme for {user_id}: {e}")
            return False
    
    @staticmethod
    def get_user_theme(user_id):
        user = DB.get_user(user_id)
        return user['theme'] if user else 'light'
