import sqlite3
import logging
import os
from threading import Lock
from datetime import datetime, timedelta
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Smart DB path handling
if os.getenv("RENDER"):
    DB_PATH = "/opt/render/project/src/data/bot65.db"
else:
    DB_PATH = os.getenv("DB_PATH", "data/bot65.db")

class DB:
    _lock = Lock()
    _connection_pool = []
    _pool_size = 5
    _initialized = False

    @staticmethod
    @contextmanager
    def conn():
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
            except Exception as e:
                logger.error(f"Failed to create DB directory: {e}")
        
        c = None
        with DB._lock:
            if DB._connection_pool:
                c = DB._connection_pool.pop()
        
        if c is None:
            c = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
            c.row_factory = sqlite3.Row
            c.execute('PRAGMA journal_mode=WAL')
            c.execute('PRAGMA synchronous=NORMAL')
            c.execute('PRAGMA cache_size=10000')
            c.execute('PRAGMA temp_store=MEMORY')
        
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
                # Users table
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

                # History table
                c.execute('''CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    game TEXT,
                    points INTEGER,
                    won INTEGER,
                    played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )''')

                # Indexes
                c.execute('CREATE INDEX IF NOT EXISTS idx_points ON users(points DESC)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_activity ON users(activity DESC)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_history_user ON history(user_id)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_history_game ON history(game)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_history_played ON history(played DESC)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_user_game ON history(user_id, game)')
                
                c.execute('PRAGMA foreign_keys = ON')
                
                row = c.execute('SELECT COUNT(*) as count FROM users').fetchone()
                user_count = row['count'] if row else 0

            DB._initialized = True
            logger.info(f"Database initialized at: {DB_PATH}")
            logger.info(f"Registered users: {user_count}")
        except Exception as e:
            logger.error(f"Database init failed: {e}")
            raise
    
    @staticmethod
    def get_user(user_id):
        try:
            with DB.conn() as c:
                row = c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None
    
    @staticmethod
    def register_user(user_id, name):
        try:
            with DB.conn() as c:
                existing = c.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,)).fetchone()
                
                if existing:
                    c.execute('''UPDATE users SET name = ?, activity = CURRENT_TIMESTAMP 
                                WHERE user_id = ?''', (name, user_id))
                    logger.info(f"Updated user: {user_id} - {name}")
                else:
                    c.execute('''INSERT INTO users (user_id, name) VALUES (?, ?)''',
                             (user_id, name))
                    logger.info(f"Registered new user: {user_id} - {name}")
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
            logger.error(f"Error updating activity {user_id}: {e}")
    
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
            
            logger.info(f"Added points to {user_id}: {points} ({game_name})")
            return True
        except Exception as e:
            logger.error(f"Error adding points to {user_id}: {e}")
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
            logger.error(f"Error fetching leaderboard: {e}")
            return []
    
    @staticmethod
    def set_theme(user_id, theme):
        try:
            with DB.conn() as c:
                c.execute('''UPDATE users SET theme = ?, activity = CURRENT_TIMESTAMP 
                            WHERE user_id = ?''', 
                         (theme, user_id))
            logger.info(f"Updated theme for {user_id}: {theme}")
            return True
        except Exception as e:
            logger.error(f"Error setting theme for {user_id}: {e}")
            return False
    
    @staticmethod
    def get_user_theme(user_id):
        user = DB.get_user(user_id)
        return user['theme'] if user else 'light'
    
    @staticmethod
    def cleanup_inactive_users(days=7):
        """Remove users inactive for specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            with DB.conn() as c:
                # Delete history first (foreign key)
                c.execute('''DELETE FROM history WHERE user_id IN (
                            SELECT user_id FROM users 
                            WHERE activity < ?
                        )''', (cutoff_date,))
                
                # Delete inactive users
                result = c.execute('''DELETE FROM users 
                                     WHERE activity < ?''', 
                                  (cutoff_date,))
                deleted = result.rowcount
            
            logger.info(f"Cleaned up {deleted} inactive users (older than {days} days)")
            return deleted
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0
    
    @staticmethod
    def backup_database():
        """Create database backup"""
        try:
            import shutil
            backup_path = DB_PATH + '.backup'
            shutil.copy2(DB_PATH, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    @staticmethod
    def get_stats():
        """Get database statistics"""
        try:
            with DB.conn() as c:
                users_count = c.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
                games_count = c.execute('SELECT COUNT(*) as count FROM history').fetchone()['count']
                total_points = c.execute('SELECT SUM(points) as total FROM users').fetchone()['total'] or 0
                
                # Get inactive users count (7 days)
                cutoff = datetime.now() - timedelta(days=7)
                inactive_count = c.execute(
                    'SELECT COUNT(*) as count FROM users WHERE activity < ?', 
                    (cutoff,)
                ).fetchone()['count']
                
                return {
                    'users': users_count,
                    'games': games_count,
                    'total_points': total_points,
                    'inactive_users': inactive_count,
                    'db_path': DB_PATH,
                    'db_size': os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return None
