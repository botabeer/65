"""
Bot 65 - Database Module
قاعدة بيانات شاملة ومختصرة
"""
import sqlite3
import logging
from threading import Lock
from datetime import datetime, timedelta
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DB:
    """نظام قاعدة البيانات الموحد"""
    _lock = Lock()
    
    @staticmethod
    @contextmanager
    def conn():
        """اتصال قاعدة البيانات"""
        c = sqlite3.connect('bot65.db', check_same_thread=False, timeout=10)
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
        """تهيئة قاعدة البيانات"""
        with DB.conn() as c:
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    points INTEGER DEFAULT 0,
                    games INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    theme TEXT DEFAULT 'light',
                    activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    game TEXT,
                    points INTEGER,
                    won INTEGER,
                    played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            c.execute('CREATE INDEX IF NOT EXISTS idx_points ON users(points DESC)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_history ON history(user_id, played DESC)')
            c.execute('PRAGMA foreign_keys = ON')
        logger.info("Database initialized")
    
    @staticmethod
    def register_user(user_id, name):
        """تسجيل مستخدم"""
        with DB._lock, DB.conn() as c:
            c.execute('''
                INSERT INTO users (user_id, name, activity)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    name = excluded.name,
                    activity = CURRENT_TIMESTAMP
            ''', (user_id, name))
    
    @staticmethod
    def get_user(user_id):
        """الحصول على بيانات المستخدم"""
        with DB.conn() as c:
            row = c.execute('''
                SELECT name, points, games, wins, theme
                FROM users WHERE user_id = ?
            ''', (user_id,)).fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def update_activity(user_id):
        """تحديث آخر نشاط"""
        with DB.conn() as c:
            c.execute('UPDATE users SET activity = CURRENT_TIMESTAMP WHERE user_id = ?', (user_id,))
    
    @staticmethod
    def add_points(user_id, points, won, game_type):
        """إضافة نقاط"""
        with DB._lock, DB.conn() as c:
            c.execute('''
                UPDATE users
                SET points = points + ?,
                    games = games + 1,
                    wins = wins + ?,
                    activity = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (points, 1 if won else 0, user_id))
            c.execute('''
                INSERT INTO history (user_id, game, points, won)
                VALUES (?, ?, ?, ?)
            ''', (user_id, game_type, points, won))
    
    @staticmethod
    def get_leaderboard(limit=20):
        """لوحة الصدارة"""
        with DB.conn() as c:
            rows = c.execute('''
                SELECT name, points, games, wins
                FROM users
                WHERE games > 0
                ORDER BY points DESC, wins DESC
                LIMIT ?
            ''', (limit,)).fetchall()
            return [dict(r) for r in rows]
    
    @staticmethod
    def set_theme(user_id, theme):
        """تغيير الثيم"""
        with DB.conn() as c:
            c.execute('UPDATE users SET theme = ? WHERE user_id = ?', (theme, user_id))
    
    @staticmethod
    def cleanup_inactive(days=30):
        """حذف المستخدمين غير النشطين"""
        with DB._lock, DB.conn() as c:
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            c.execute('DELETE FROM users WHERE activity < ?', (cutoff,))
            deleted = c.rowcount
            if deleted > 0:
                logger.info(f"Cleaned {deleted} inactive users")
