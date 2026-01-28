import sqlite3
import os
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path="preddit.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Threads table: Stores post metadata
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threads (
                    reddit_id TEXT PRIMARY KEY,
                    subreddit TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    score INTEGER,
                    author TEXT,
                    timestamp INTEGER,
                    comment_url TEXT,
                    fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Fetch log: Tracks scraping attempts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fetch_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subreddit TEXT NOT NULL,
                    status TEXT,
                    count INTEGER,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def save_threads(self, threads_data):
        """Saves a list of thread dictionaries to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            saved_count = 0
            for thread in threads_data:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO threads (
                            reddit_id, subreddit, title, url, score, author, timestamp, comment_url
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        thread['reddit_id'], thread['subreddit'], thread['title'], 
                        thread['url'], thread['score'], thread['author'], 
                        thread['timestamp'], thread['comment_url']
                    ))
                    if cursor.rowcount > 0:
                        saved_count += 1
                except Exception as e:
                    print(f"Error saving thread {thread.get('reddit_id')}: {e}")
            conn.commit()
            return saved_count

    def log_fetch(self, subreddit, status, count, error_message=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO fetch_log (subreddit, status, count, error_message)
                VALUES (?, ?, ?, ?)
            ''', (subreddit, status, count, error_message))
            conn.commit()

    def get_last_fetch_time(self, subreddit):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp FROM fetch_log 
                WHERE subreddit = ? AND status = 'success' 
                ORDER BY timestamp DESC LIMIT 1
            ''', (subreddit,))
            row = cursor.fetchone()
            if row:
                # SQLite timestamp is string 'YYYY-MM-DD HH:MM:SS'
                try: return datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                except: return None
            return None

    def get_threads(self, subreddit=None, limit=50):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if subreddit:
                cursor.execute('''
                    SELECT * FROM threads WHERE subreddit = ? 
                    ORDER BY timestamp DESC LIMIT ?
                ''', (subreddit, limit))
            else:
                cursor.execute('''
                    SELECT * FROM threads 
                    ORDER BY fetch_date DESC LIMIT ?
                ''', (limit,))
            # Convert to list of dicts for easier handling in templates
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def cleanup_old_threads(self, days=30):
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM threads WHERE fetch_date < ?', (cutoff,))
            count = cursor.rowcount
            conn.commit()
            return count
