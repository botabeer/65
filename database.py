import sqlite3
import logging
import os
from threading import Lock
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "bot65.db")

class DB:
    _lock = Lock()

    @staticmethod
    @contextmanager
    def conn():
        os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else '.', exist_ok=True)
        c = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
        c.row_factory = sqlite3.Row
        try:
            yield c
            c.commit()
        except:
            c.rollback()
            raise
        finally:
            c.close()

    @staticmethod
    def init():
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
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )''')

            c.execute('CREATE INDEX IF NOT EXISTS idx_points ON users(points DESC)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_history ON history(user_id, played DESC)')
            c.execute('PRAGMA foreign_keys = ON')

        logger.info("Database initialized")
    
    @staticmethod
    def get_user(user_id):
        with DB.conn() as c:
            row = c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def register_user(user_id, name):
        with DB.conn() as c:
            c.execute('''INSERT INTO users (user_id, name) VALUES (?, ?)
                        ON CONFLICT(user_id) DO UPDATE SET name = ?''',
                     (user_id, name, name))
    
    @staticmethod
    def update_activity(user_id):
        with DB.conn() as c:
            c.execute('UPDATE users SET activity = CURRENT_TIMESTAMP WHERE user_id = ?', (user_id,))
    
    @staticmethod
    def add_points(user_id, points, won, game_name):
        with DB.conn() as c:
            c.execute('''UPDATE users SET 
                        points = points + ?,
                        games = games + 1,
                        wins = wins + ?
                        WHERE user_id = ?''', (points, 1 if won else 0, user_id))
            c.execute('INSERT INTO history (user_id, game, points, won) VALUES (?, ?, ?, ?)',
                     (user_id, game_name, points, 1 if won else 0))
    
    @staticmethod
    def get_leaderboard(limit=20):
        with DB.conn() as c:
            rows = c.execute('SELECT * FROM users ORDER BY points DESC LIMIT ?', (limit,)).fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def set_theme(user_id, theme):
        with DB.conn() as c:
            c.execute('UPDATE users SET theme = ? WHERE user_id = ?', (theme, user_id))
    
    @staticmethod
    def get_user_theme(user_id):
        user = DB.get_user(user_id)
        return user['theme'] if user else 'light'


class Database:
    @staticmethod
    def get_user_theme(user_id):
        return DB.get_user_theme(user_id)
    
    @staticmethod
    def update_user_points(user_id, points, won, game_name):
        DB.add_points(user_id, points, won, game_name)
