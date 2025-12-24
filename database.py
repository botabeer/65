import sqlite3
import logging
import os
from threading import Lock
from datetime import datetime, timedelta
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "/data/bot65.db")

class DB:
    _lock = Lock()

    @staticmethod
    @contextmanager
    def conn():
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
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
