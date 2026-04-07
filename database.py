import sqlite3
import json
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import secrets

class DatabaseManager:
    def __init__(self, db_path: str = None):
        # Use /tmp for Vercel serverless environment
        if db_path is None:
            if os.environ.get('VERCEL'):
                self.db_path = "/tmp/wellness_data.db"
            else:
                self.db_path = "wellness_data.db"
        else:
            self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table with authentication
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    username TEXT UNIQUE,
                    email TEXT UNIQUE,
                    firebase_uid TEXT UNIQUE,
                    profile_photo TEXT,
                    auth_provider TEXT DEFAULT 'local',
                    password_hash TEXT,
                    salt TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Mood entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mood_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    date DATE,
                    mood_score INTEGER,
                    screen_time_hours REAL,
                    app_usage_minutes INTEGER,
                    sleep_hours REAL,
                    social_media_hours REAL,
                    work_hours REAL,
                    gaming_hours REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # User progress table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    date DATE,
                    tasks_completed INTEGER,
                    total_tasks INTEGER,
                    streak_days INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_mood_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    date DATE,
                    mood_label TEXT,
                    mood_score REAL,
                    note TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, date),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Screen time tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS screen_time (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    date DATE,
                    hours REAL,
                    app_sessions INTEGER,
                    notifications INTEGER,
                    night_usage REAL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Sleep tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sleep_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    date DATE,
                    quality_score REAL,
                    hours_slept REAL,
                    bedtime TIME,
                    wake_time TIME,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Education progress table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS education_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    article_id INTEGER,
                    path_level TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    completion_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # User goals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    goal_type TEXT,
                    target_value REAL,
                    current_value REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Streaks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS streaks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    current_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0,
                    last_activity_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Achievements table (definitions)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    achievement_id TEXT UNIQUE,
                    title TEXT,
                    description TEXT,
                    icon TEXT,
                    unlock_condition TEXT,
                    points_reward INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User achievements table (tracking)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    achievement_id TEXT,
                    unlocked BOOLEAN DEFAULT 0,
                    unlock_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (achievement_id) REFERENCES achievements (achievement_id)
                )
            ''')
            
            # User points table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_points (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    total_points INTEGER DEFAULT 0,
                    points_this_month INTEGER DEFAULT 0,
                    points_this_week INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Points transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS points_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    points INTEGER,
                    reason TEXT,
                    date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # User tasks table (for daily wellness tasks)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    task_name TEXT,
                    points INTEGER,
                    completed BOOLEAN DEFAULT 0,
                    completed_at TIMESTAMP,
                    date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Wellness tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wellness_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name TEXT,
                    task_type TEXT,
                    duration_minutes INTEGER,
                    difficulty_level TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Initialize default wellness tasks
            cursor.execute("SELECT COUNT(*) FROM wellness_tasks")
            task_count = cursor.fetchone()[0]
            
            if task_count == 0:
                default_tasks = [
                    ("Morning Meditation", "mindfulness", 10, "easy", "Start your day with 10 minutes of mindful meditation"),
                    ("Digital Detox Hour", "detox", 60, "medium", "Spend one hour completely away from screens"),
                    ("Evening Walk", "physical", 30, "easy", "Take a 30-minute walk without your phone"),
                    ("Read a Book", "learning", 45, "medium", "Read a physical book for 45 minutes"),
                    ("No Social Media", "detox", 1440, "hard", "Avoid social media for the entire day"),
                    ("Stretch Break", "physical", 15, "easy", "Take regular stretch breaks every hour"),
                    ("Journal Before Bed", "mindfulness", 20, "easy", "Write in a journal before sleeping")
                ]
                
                cursor.executemany('''
                    INSERT INTO wellness_tasks (task_name, task_type, duration_minutes, difficulty_level, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', default_tasks)
            
            conn.commit()
            self._run_migrations(conn)
            conn.close()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise e

    def _run_migrations(self, conn):
        """Apply lightweight SQLite migrations."""
        cursor = conn.cursor()
        self._ensure_column(cursor, "users", "firebase_uid", "TEXT")
        self._ensure_column(cursor, "users", "profile_photo", "TEXT")
        self._ensure_column(cursor, "users", "auth_provider", "TEXT DEFAULT 'local'")
        self._ensure_column(cursor, "mood_entries", "mood_label", "TEXT")
        self._ensure_column(cursor, "mood_entries", "note", "TEXT")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_firebase_uid ON users(firebase_uid)")
        cursor.execute(
            '''
            DELETE FROM user_achievements
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM user_achievements
                GROUP BY user_id, achievement_id
            )
            '''
        )
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_user_achievement_unique ON user_achievements(user_id, achievement_id)"
        )
        cursor.execute(
            '''
            DELETE FROM points_transactions
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM points_transactions
                WHERE reason LIKE 'Achievement unlocked:%'
                GROUP BY user_id, reason
            )
            AND reason LIKE 'Achievement unlocked:%'
            '''
        )
        cursor.execute(
            "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
            ("2026_04_firebase_auth",)
        )
        conn.commit()

    def _ensure_column(self, cursor, table_name: str, column_name: str, column_def: str):
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {row[1] for row in cursor.fetchall()}
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
    
    def get_or_create_user(self, user_id: str) -> int:
        """Get existing user or create new one"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        if not result:
            cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

        cursor.execute(
            "INSERT OR IGNORE INTO streaks (user_id, current_streak, longest_streak) VALUES (?, 0, 0)",
            (user_id,)
        )

        cursor.execute(
            "INSERT OR IGNORE INTO user_points (user_id, total_points, points_this_month, points_this_week) VALUES (?, 0, 0, 0)",
            (user_id,)
        )

        cursor.execute("SELECT achievement_id FROM achievements")
        achievements = cursor.fetchall()
        for achievement in achievements:
            cursor.execute(
                "INSERT OR IGNORE INTO user_achievements (user_id, achievement_id, unlocked) VALUES (?, ?, 0)",
                (user_id, achievement[0])
            )

        conn.commit()
        
        conn.close()
        return result[0] if result else None

    def create_or_update_firebase_user(self, firebase_uid: str, email: str, username: str = None) -> Dict:
        """Create or update a user authenticated via Firebase."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        normalized_email = (email or "").strip().lower()
        resolved_username = (username or normalized_email.split("@")[0] or "wellness_user").strip()

        try:
            cursor.execute(
                '''
                SELECT user_id, username, email, firebase_uid
                FROM users
                WHERE firebase_uid = ? OR email = ?
                ''',
                (firebase_uid, normalized_email)
            )
            existing = cursor.fetchone()

            if existing:
                user_id, existing_username, existing_email, _ = existing
                cursor.execute(
                    '''
                    UPDATE users
                    SET firebase_uid = ?, email = ?, username = COALESCE(username, ?),
                        auth_provider = 'firebase', last_active = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                    ''',
                    (firebase_uid, normalized_email or existing_email, resolved_username, user_id)
                )
            else:
                user_id = f"user_{secrets.token_hex(8)}"
                final_username = self._make_unique_username(cursor, resolved_username)
                cursor.execute(
                    '''
                    INSERT INTO users (user_id, username, email, firebase_uid, auth_provider)
                    VALUES (?, ?, ?, ?, 'firebase')
                    ''',
                    (user_id, final_username, normalized_email, firebase_uid)
                )

            conn.commit()
            self.get_or_create_user(user_id)
            return self.get_user_by_id(user_id)
        finally:
            conn.close()

    def _make_unique_username(self, cursor, base_username: str) -> str:
        candidate = "".join(ch for ch in base_username if ch.isalnum() or ch in {"_", "-"}) or "wellness_user"
        suffix = 1
        while True:
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (candidate,))
            if not cursor.fetchone():
                return candidate
            candidate = f"{base_username}_{suffix}"
            suffix += 1

    
    def save_mood_entry(self, user_id: str, mood: str, score: float, note: str = None) -> bool:
        """Save mood entry and update streak"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Save mood entry with correct columns
            cursor.execute(
                '''
                INSERT INTO mood_entries (user_id, date, mood_score, mood_label, note, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''',
                (user_id, datetime.now().date(), score, mood, note)
            )
            
            # Update streak
            self._update_streak(cursor, user_id)
            
            # Update last active
            cursor.execute('''
                UPDATE users SET last_active = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving mood entry: {e}")
            return False
        finally:
            conn.close()
    
    def _update_streak(self, cursor, user_id: str):
        """Update user streak based on daily activity"""
        today = datetime.now().date()
        
        cursor.execute('''
            SELECT last_activity_date, current_streak, longest_streak 
            FROM streaks WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        if not result:
            # First activity - start streak at 1
            cursor.execute('''
                INSERT INTO streaks (user_id, current_streak, longest_streak, last_activity_date)
                VALUES (?, 1, 1, ?)
            ''', (user_id, today))
            return
        
        last_activity, current_streak, longest_streak = result
        
        if last_activity:
            last_date = datetime.strptime(last_activity, '%Y-%m-%d').date()
            days_diff = (today - last_date).days
            
            if days_diff == 0:
                # Same day activity - don't increment streak but ensure it's at least 1
                if current_streak == 0:
                    new_streak = 1
                else:
                    new_streak = current_streak
            elif days_diff == 1:
                # Consecutive day - increment streak
                new_streak = current_streak + 1
            else:
                # Streak broken - start new streak
                new_streak = 1
        else:
            # First activity
            new_streak = 1
        
        cursor.execute('''
            UPDATE streaks 
            SET current_streak = ?, longest_streak = ?, last_activity_date = ?
            WHERE user_id = ?
        ''', (new_streak, max(longest_streak, new_streak), today, user_id))
    
    def get_streak_data(self, user_id: str) -> Dict:
        """Get current streak data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT current_streak, longest_streak, last_activity_date 
            FROM streaks WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            current_streak, longest_streak, last_activity = result
            
            # Calculate completion rate for this week
            completion_summary = self.get_completion_summary(user_id, 7)
            
            return {
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'last_activity': last_activity,
                'completion_rate': completion_summary['completion_rate'],
                'tasks_completed': completion_summary['completed_tasks'],
                'active_days': completion_summary['active_days']
            }
        
        return {'current_streak': 0, 'longest_streak': 0, 'completion_rate': 0, 'tasks_completed': 0, 'active_days': 0}
    
    def _calculate_weekly_completion(self, user_id: str) -> float:
        """Calculate weekly task completion rate based on completed task instances."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            week_ago = (datetime.now() - timedelta(days=6)).date()
            available_tasks_per_day = max(len(self.get_wellness_tasks()), 1)
            total_available = available_tasks_per_day * 7

            cursor.execute(
                '''
                SELECT COUNT(*)
                FROM user_tasks
                WHERE user_id = ? AND date >= ? AND completed = 1
                ''',
                (user_id, week_ago),
            )

            completed_total = cursor.fetchone()[0] or 0
            completion_rate = (completed_total / total_available) * 100 if total_available else 0
            return round(min(100, completion_rate), 2)
        finally:
            conn.close()
    
    def complete_wellness_task(self, user_id: str, task_name: str) -> bool:
        """Mark a wellness task as completed"""
        return self.save_wellness_task(user_id, task_name, 10, completed=True)
    
    def save_wellness_task(self, user_id: str, task_name: str, points: int, completed: bool = True) -> bool:
        """Save wellness task completion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            today = datetime.now().date()
            
            # Check if task already exists for today
            cursor.execute('''
                SELECT id FROM user_tasks 
                WHERE user_id = ? AND task_name = ? AND date = ?
            ''', (user_id, task_name, today))
            
            existing = cursor.fetchone()
            
            was_completed = False

            if existing:
                cursor.execute("SELECT completed FROM user_tasks WHERE id = ?", (existing[0],))
                status_row = cursor.fetchone()
                was_completed = bool(status_row[0]) if status_row else False

                # Update existing task - only update completed status, preserve timestamp
                if completed:
                    cursor.execute('''
                        UPDATE user_tasks 
                        SET completed = 1, completed_at = ?
                        WHERE id = ?
                    ''', (datetime.now(), existing[0]))
                else:
                    cursor.execute('''
                        UPDATE user_tasks 
                        SET completed = 0, completed_at = NULL
                        WHERE id = ?
                    ''', (existing[0],))
            else:
                # Insert new task
                cursor.execute('''
                    INSERT INTO user_tasks (user_id, task_name, points, completed, completed_at, date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, task_name, points, completed, datetime.now() if completed else None, today))
            
            # Update points and streak
            if completed and not was_completed:
                self._add_points(cursor, user_id, points, f"Completed task: {task_name}")
            elif not completed and was_completed:
                self._add_points(cursor, user_id, -abs(points), f"Reopened task: {task_name}")
            
            # Always update streak (tracks activity, not just completion)
            self._update_streak(cursor, user_id)
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving wellness task: {e}")
            return False
        finally:
            conn.close()
    
    def get_wellness_tasks(self, user_id: str = None) -> List[Dict]:
        """Get wellness tasks - if user_id provided, get user's tasks, otherwise get all available tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            # Get user's tasks for today
            today = datetime.now().date()
            
            cursor.execute('''
                SELECT task_name, points, completed, completed_at
                FROM user_tasks 
                WHERE user_id = ? AND date = ?
                ORDER BY task_name
            ''', (user_id, today))
            
            user_tasks = []
            for row in cursor.fetchall():
                user_tasks.append({
                    'task_name': row[0],
                    'points': row[1],
                    'completed': bool(row[2]),
                    'completed_at': row[3]
                })
            
            conn.close()
            return user_tasks
        else:
            # Get all available wellness tasks
            cursor.execute('''
                SELECT task_name, task_type, duration_minutes, difficulty_level, description
                FROM wellness_tasks
                ORDER BY task_type, task_name
            ''')
            
            available_tasks = []
            for row in cursor.fetchall():
                available_tasks.append({
                    'task_name': row[0],
                    'task_type': row[1],
                    'duration_minutes': row[2],
                    'difficulty_level': row[3],
                    'description': row[4],
                    'points': 10  # Default points
                })
            
            conn.close()
            return available_tasks

    def get_task_summary(self, user_id: str) -> Dict:
        """Return a compact summary of today's task and mood activity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''
                SELECT COUNT(*) FROM user_tasks
                WHERE user_id = ? AND completed = 1 AND date = date('now')
                ''',
                (user_id,)
            )
            completed_tasks = cursor.fetchone()[0] or 0

            cursor.execute(
                '''
                SELECT COUNT(*) FROM mood_entries
                WHERE user_id = ? AND DATE(created_at) = date('now')
                ''',
                (user_id,)
            )
            mood_checkins = cursor.fetchone()[0] or 0

            return {
                "daily_tasks": completed_tasks,
                "mood_checkins": mood_checkins,
            }
        finally:
            conn.close()

    def get_completion_summary(self, user_id: str, days: int = 7) -> Dict:
        """Return completion totals for the recent period."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        start_date = (datetime.now() - timedelta(days=max(days - 1, 0))).date()
        available_tasks_per_day = max(len(self.get_wellness_tasks()), 1)
        total_available = available_tasks_per_day * max(days, 1)

        try:
            cursor.execute(
                '''
                SELECT COUNT(*), COUNT(DISTINCT date)
                FROM user_tasks
                WHERE user_id = ? AND completed = 1 AND date >= ?
                ''',
                (user_id, start_date),
            )
            completed_count, active_days = cursor.fetchone()
            completed_count = completed_count or 0
            active_days = active_days or 0

            return {
                "completed_tasks": completed_count,
                "active_days": active_days,
                "available_tasks": total_available,
                "completion_rate": round((completed_count / total_available) * 100, 2) if total_available else 0,
            }
        finally:
            conn.close()

    def get_daily_task_completion(self, user_id: str, total_tasks: int = 6) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''
                SELECT COUNT(*)
                FROM user_tasks
                WHERE user_id = ? AND completed = 1 AND date = date('now')
                ''',
                (user_id,)
            )
            completed = cursor.fetchone()[0] or 0
            rate = round((completed / total_tasks) * 100, 2) if total_tasks else 0
            return {
                "completed_tasks": completed,
                "total_tasks": total_tasks,
                "completion_rate": min(100, rate),
            }
        finally:
            conn.close()
    
    def get_historical_data(self, user_id: str, days: int = 7) -> Dict:
        """Get historical data for dashboard charts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=max(days - 1, 0))).date()
        period_dates = [(start_date + timedelta(days=offset)) for offset in range(days)]
        available_tasks_per_day = max(len(self.get_wellness_tasks()), 1)

        try:
            cursor.execute(
                '''
                SELECT date, AVG(mood_score) as avg_score
                FROM mood_entries
                WHERE user_id = ? AND date >= ?
                GROUP BY date
                ORDER BY date
                ''',
                (user_id, start_date),
            )
            mood_lookup = {row[0]: round(row[1], 1) for row in cursor.fetchall()}

            cursor.execute(
                '''
                SELECT date, hours
                FROM screen_time
                WHERE user_id = ? AND date >= ?
                ORDER BY date
                ''',
                (user_id, start_date),
            )
            screen_lookup = {row[0]: round(row[1], 1) for row in cursor.fetchall()}

            cursor.execute(
                '''
                SELECT date, quality_score
                FROM sleep_data
                WHERE user_id = ? AND date >= ?
                ORDER BY date
                ''',
                (user_id, start_date),
            )
            sleep_lookup = {row[0]: round(row[1], 1) for row in cursor.fetchall()}

            cursor.execute(
                '''
                SELECT date, COUNT(*), SUM(points)
                FROM user_tasks
                WHERE user_id = ? AND completed = 1 AND date >= ?
                GROUP BY date
                ORDER BY date
                ''',
                (user_id, start_date),
            )
            task_rows = cursor.fetchall()
            task_count_lookup = {row[0]: row[1] or 0 for row in task_rows}
            points_lookup = {row[0]: row[2] or 0 for row in task_rows}

            mood_data = []
            screen_time_data = []
            sleep_data = []
            completion_data = []
            points_data = []
            focus_data = []

            for period_date in period_dates:
                key = period_date.strftime('%Y-%m-%d')
                label = self._format_date_label(period_date, days)
                mood_value = mood_lookup.get(key, 0)
                screen_value = screen_lookup.get(key, 0)
                sleep_value = sleep_lookup.get(key, 0)
                completed_tasks = task_count_lookup.get(key, 0)
                points_value = points_lookup.get(key, 0)
                completion_value = round((completed_tasks / available_tasks_per_day) * 100, 1)

                if mood_value and sleep_value:
                    focus_value = round(max(0, min(100, ((mood_value / 5) * 45) + ((sleep_value / 10) * 35) + (max(0, 8 - screen_value) / 8) * 20)), 1)
                elif mood_value or sleep_value or screen_value:
                    focus_value = round(max(0, min(100, ((mood_value or 3) / 5) * 40 + ((sleep_value or 5) / 10) * 35 + (max(0, 8 - (screen_value or 4)) / 8) * 25)), 1)
                else:
                    focus_value = 0

                mood_data.append({"date": label, "value": mood_value})
                screen_time_data.append({"date": label, "value": screen_value})
                sleep_data.append({"date": label, "value": sleep_value})
                completion_data.append({"date": label, "value": completion_value})
                points_data.append({"date": label, "value": points_value})
                focus_data.append({"date": label, "value": focus_value})

            return {
                'mood_trend': mood_data,
                'stress_vs_screen_time': screen_time_data,
                'sleep_vs_mental_fatigue': sleep_data,
                'task_completion': completion_data,
                'points_earned': points_data,
                'usage_vs_concentration': focus_data
            }
        finally:
            conn.close()

    def _format_date_label(self, date_input, days: int) -> str:
        """Format date label based on the period"""
        # Convert string to date object if needed
        if isinstance(date_input, str):
            try:
                from datetime import datetime
                date_obj = datetime.strptime(date_input, '%Y-%m-%d').date()
            except:
                # If parsing fails, use today's date
                date_obj = datetime.now().date()
        else:
            date_obj = date_input
        
        if days >= 30:
            # For month view, show month abbreviations
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            return month_names[date_obj.month - 1]
        else:
            # For week view, show day abbreviations
            return date_obj.strftime('%a')

    def _generate_sample_data(self, days: int, data_type: str) -> List[Dict]:
        """Generate sample data for demonstration"""
        import random
        data = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1)).date()
            date_label = self._format_date_label(date, days)
            
            if data_type == 'mood':
                value = random.uniform(2.5, 5.0)
            elif data_type == 'screen_time':
                value = random.uniform(20, 80)  # Chart scale
            elif data_type == 'sleep':
                value = random.uniform(5, 9)
            else:
                value = random.uniform(1, 10)
            
            data.append({
                'date': date_label,
                'value': round(value, 1)
            })
        
        return data
    
    def _generate_focus_data(self, days: int) -> List[Dict]:
        """Generate focus data based on recent activity"""
        import random
        data = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1)).date()
            date_label = self._format_date_label(date, days)
            data.append({
                'date': date_label,
                'value': random.uniform(1, 10)
            })
        return data
    
    def save_screen_time(self, user_id: str, hours: float, app_sessions: int = 0, notifications: int = 0, night_usage: float = 0) -> bool:
        """Save screen time data for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            today = datetime.now().date()
            
            # Check if entry exists for today
            cursor.execute('''
                SELECT id FROM screen_time 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing entry
                cursor.execute('''
                    UPDATE screen_time 
                    SET hours = ?, app_sessions = ?, notifications = ?, night_usage = ?
                    WHERE user_id = ? AND date = ?
                ''', (hours, app_sessions, notifications, night_usage, user_id, today))
            else:
                # Insert new entry
                cursor.execute('''
                    INSERT INTO screen_time (user_id, date, hours, app_sessions, notifications, night_usage)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, today, hours, app_sessions, notifications, night_usage))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving screen time: {e}")
            return False
        finally:
            conn.close()
    
    def save_sleep_data(self, user_id: str, hours_slept: float, quality_score: float = 5.0, bedtime: str = None, wake_time: str = None) -> bool:
        """Save sleep data for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            today = datetime.now().date()
            
            # Check if entry exists for today
            cursor.execute('''
                SELECT id FROM sleep_data 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing entry
                cursor.execute('''
                    UPDATE sleep_data 
                    SET hours_slept = ?, quality_score = ?, bedtime = ?, wake_time = ?
                    WHERE user_id = ? AND date = ?
                ''', (hours_slept, quality_score, bedtime, wake_time, user_id, today))
            else:
                # Insert new entry
                cursor.execute('''
                    INSERT INTO sleep_data (user_id, date, hours_slept, quality_score, bedtime, wake_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, today, hours_slept, quality_score, bedtime, wake_time))
            
            conn.commit()
            
            # Update streak if good sleep
            if quality_score >= 7:
                self._update_streak_for_user(user_id)
            
            return True
        except Exception as e:
            print(f"Error saving sleep data: {e}")
            return False
        finally:
            conn.close()
    
    def save_mood_data(self, user_id: str, mood_score: float, note: str = None):
        """Save mood data for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO mood_entries (user_id, mood_score, created_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, mood_score))
            
            conn.commit()
            
            # Update streak for mood check-in
            self._update_streak_for_user(user_id)
            
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving mood data: {e}")
            return False
        finally:
            conn.close()
    
    def _update_streak_for_user(self, user_id: str):
        """Update streak for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            self._update_streak(cursor, user_id)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error updating streak: {e}")
        finally:
            conn.close()
        
    def get_dashboard_metrics(self, user_id: str) -> Dict:
        """Calculate dashboard metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent mood average
        cursor.execute('''
            SELECT AVG(mood_score) as avg_mood 
            FROM mood_entries 
            WHERE user_id = ? AND date >= ?
        ''', (user_id, (datetime.now() - timedelta(days=7)).date()))
        
        mood_result = cursor.fetchone()
        avg_mood = mood_result[0] if mood_result and mood_result[0] else 3.5
        
        # Get today's screen time
        today = datetime.now().date()
        cursor.execute('''
            SELECT hours FROM screen_time 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        
        screen_time_result = cursor.fetchone()
        daily_screen_time = screen_time_result[0] if screen_time_result else 0
        
        completion_summary = self.get_completion_summary(user_id, 7)

        # Get wellness score
        streak_data = self.get_streak_data(user_id)
        
        # Calculate overall wellbeing score
        # completion_rate is 0-100, so divide by 100 to scale to 0-1 for 40-point contribution
        wellbeing_score = min(100, round(
            (avg_mood / 5.0) * 40 +  # Mood contribution (0-40)
            (completion_summary['completion_rate'] / 100.0) * 40 +  # Completion contribution (0-40)
            (1 - min(daily_screen_time / 8, 1)) * 20  # Screen time contribution (0-20)
        ))
        
        conn.close()
        
        return {
            'wellbeing_score': wellbeing_score,
            'avg_mood': round(avg_mood, 1),
            'daily_screen_time': daily_screen_time,
            'streak': streak_data['current_streak'],
            'completion_rate': completion_summary['completion_rate']
        }
    
    def save_education_progress(self, user_id: str, article_id: int, path_level: str) -> bool:
        """Save education progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO education_progress 
                (user_id, article_id, path_level, completed, completion_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, article_id, path_level, True, datetime.now()))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving education progress: {e}")
            return False
        finally:
            conn.close()
    
    def get_education_progress(self, user_id: str) -> Dict:
        """Get education progress data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT path_level, COUNT(*) as completed
            FROM education_progress 
            WHERE user_id = ? AND completed = 1
            GROUP BY path_level
        ''', (user_id,))
        
        progress = {}
        for row in cursor.fetchall():
            progress[row[0]] = row[1]
        
        conn.close()
        return progress
    
    # Authentication methods
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user with authentication"""
        import hashlib
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Generate password hash
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            # Generate unique user_id
            user_id = f"user_{secrets.token_hex(8)}"
            
            cursor.execute('''
                INSERT INTO users (user_id, username, email, password_hash, salt)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, email, password_hash, salt))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        import hashlib
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, email, profile_photo, password_hash, salt, last_active
            FROM users WHERE username = ? OR email = ?
        ''', (username, username))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            user_id, username, email, profile_photo, stored_hash, salt, last_active = user
            
            # Hash the provided password with the stored salt
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            if password_hash == stored_hash:
                return {
                    'user_id': user_id,
                    'username': username,
                    'email': email,
                    'profile_photo': profile_photo,
                    'last_active': last_active
                }
        
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user data by user_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, email, firebase_uid, profile_photo, auth_provider, created_at, last_active
            FROM users WHERE user_id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'firebase_uid': user[3],
                'profile_photo': user[4],
                'auth_provider': user[5],
                'created_at': user[6],
                'last_active': user[7]
            }
        
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE email = ?", ((email or "").strip().lower(),))
        row = cursor.fetchone()
        conn.close()
        return self.get_user_by_id(row[0]) if row else None

    def update_profile(self, user_id: str, username: str, email: str, profile_photo: str = "") -> tuple[bool, str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            username = (username or "").strip()
            email = (email or "").strip().lower()
            profile_photo = (profile_photo or "").strip()
            if not username or not email:
                return False, "Name and email are required"

            if profile_photo and not profile_photo.startswith("data:image/"):
                return False, "Profile photo must be a valid image"
            if len(profile_photo) > 900000:
                return False, "Profile photo is too large. Please choose a smaller image."

            cursor.execute(
                '''
                SELECT user_id FROM users
                WHERE (username = ? OR email = ?) AND user_id != ?
                ''',
                (username, email, user_id)
            )
            if cursor.fetchone():
                return False, "That username or email is already in use"

            cursor.execute(
                '''
                UPDATE users
                SET username = ?, email = ?, profile_photo = COALESCE(NULLIF(?, ''), profile_photo), last_active = CURRENT_TIMESTAMP
                WHERE user_id = ?
                ''',
                (username, email, profile_photo, user_id)
            )
            conn.commit()
            return True, "Profile updated successfully"
        except Exception as exc:
            conn.rollback()
            return False, f"Could not update profile: {exc}"
        finally:
            conn.close()

    def change_password(self, user_id: str, current_password: str, new_password: str) -> tuple[bool, str]:
        import hashlib

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''
                SELECT password_hash, salt, auth_provider
                FROM users
                WHERE user_id = ?
                ''',
                (user_id,)
            )
            row = cursor.fetchone()
            if not row:
                return False, "User not found"

            stored_hash, salt, auth_provider = row
            if auth_provider == "firebase":
                return False, "Password changes for Firebase accounts must be done through Firebase reset"

            if current_password:
                current_hash = hashlib.sha256((current_password + salt).encode()).hexdigest()
                if current_hash != stored_hash:
                    return False, "Current password is incorrect"

            new_salt = secrets.token_hex(16)
            new_hash = hashlib.sha256((new_password + new_salt).encode()).hexdigest()
            cursor.execute(
                '''
                UPDATE users
                SET password_hash = ?, salt = ?, last_active = CURRENT_TIMESTAMP
                WHERE user_id = ?
                ''',
                (new_hash, new_salt, user_id)
            )
            conn.commit()
            return True, "Password updated successfully"
        except Exception as exc:
            conn.rollback()
            return False, f"Could not change password: {exc}"
        finally:
            conn.close()

    def get_recent_moods(self, user_id: str, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT mood_label, mood_score, note, created_at
            FROM mood_entries
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            ''',
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "mood": row[0] or "saved",
                "score": row[1],
                "note": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

    def get_saved_mood_count(self, user_id: str) -> int:
        today_mood = self.get_today_mood_status(user_id)
        return 1 if today_mood else 0

    def upsert_daily_mood_status(self, user_id: str, mood: str, score: float, note: str = None) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            today = datetime.now().date()
            cursor.execute(
                '''
                INSERT INTO daily_mood_status (user_id, date, mood_label, mood_score, note, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, date) DO UPDATE SET
                    mood_label = excluded.mood_label,
                    mood_score = excluded.mood_score,
                    note = excluded.note,
                    updated_at = CURRENT_TIMESTAMP
                ''',
                (user_id, today, mood, score, note)
            )
            self._update_streak(cursor, user_id)
            conn.commit()
            return True
        except Exception as exc:
            conn.rollback()
            print(f"Error updating daily mood status: {exc}")
            return False
        finally:
            conn.close()

    def get_today_mood_status(self, user_id: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''
                SELECT mood_label, mood_score, note, updated_at
                FROM daily_mood_status
                WHERE user_id = ? AND date = date('now')
                ''',
                (user_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "mood": row[0],
                "score": row[1],
                "note": row[2],
                "updated_at": row[3],
            }
        finally:
            conn.close()

    def get_points_breakdown(self, user_id: str, days: int = 7) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        start_date = (datetime.now() - timedelta(days=max(days - 1, 0))).date()
        try:
            cursor.execute(
                '''
                SELECT
                    COALESCE(SUM(CASE WHEN reason LIKE 'Completed task:%' THEN points ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN reason LIKE 'Achievement unlocked:%' THEN points ELSE 0 END), 0),
                    COALESCE(SUM(points), 0)
                FROM points_transactions
                WHERE user_id = ? AND date >= ?
                ''',
                (user_id, start_date)
            )
            task_points, achievement_points, total_points = cursor.fetchone()
            return {
                "task_points": task_points or 0,
                "achievement_points": achievement_points or 0,
                "total_points": total_points or 0,
            }
        finally:
            conn.close()

    def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT user_id FROM users WHERE firebase_uid = ?
            ''',
            (firebase_uid,)
        )
        row = cursor.fetchone()
        conn.close()
        return self.get_user_by_id(row[0]) if row else None
    
    def update_last_active(self, user_id: str):
        """Update user's last active timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def _add_points(self, cursor, user_id: str, points: int, reason: str):
        """Add points to user (internal method using existing cursor)"""
        today = datetime.now().date()
        
        # Record transaction
        cursor.execute('''
            INSERT INTO points_transactions (user_id, points, reason, date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, points, reason, today))
        
        # Update total points
        cursor.execute('''
            UPDATE user_points 
            SET total_points = total_points + ?,
                points_this_month = points_this_month + ?,
                points_this_week = points_this_week + ?
            WHERE user_id = ?
        ''', (points, points, points, user_id))
    
    def get_user_points(self, user_id: str) -> Dict:
        """Get user's points statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT total_points, points_this_month, points_this_week
            FROM user_points WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'total_points': result[0],
                'this_month': result[1],
                'this_week': result[2]
            }
        
        return {'total_points': 0, 'this_month': 0, 'this_week': 0}
    
    def initialize_achievements(self):
        """Initialize default achievements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        achievements = [
            ('week_warrior', 'Week Warrior', '7-day streak completed', 'fa-fire', '7_day_streak', 50),
            ('sleep_champion', 'Sleep Champion', '5 nights of quality sleep', 'fa-moon', 'sleep_nights', 100),
            ('mindful_master', 'Mindful Master', 'Completed 10 mood check-ins', 'fa-brain', 'mood_checkins', 75),
            ('mindful_starter', 'Mindful Starter', 'Completed 5 mood check-ins', 'fa-brain', 'mood_checkins_5', 25),
            ('balance_score', 'Balance Score', 'Maintain 80+ wellbeing score', 'fa-scale-balanced', 'wellbeing_80', 100),
            ('task_master', 'Task Master', '10 wellness tasks completed', 'fa-tasks', 'tasks_10', 80),
            ('task_starter', 'Task Starter', '5 wellness tasks completed', 'fa-check-circle', 'tasks_5', 30),
            ('growing_strong', 'Growing Strong', '3-day streak', 'fa-heart', 'streak_3', 20),
            ('real_connections', 'Real Connections', 'Social tasks completed', 'fa-users', 'social_tasks', 80),
            ('detox_hero', 'Detox Hero', '7-day phone-free challenge', 'fa-fire-extinguisher', 'phone_free_7days', 150),
            ('digital_balance', 'Digital Balance', 'Keep screen time under 4 hours', 'fa-mobile', 'screen_time_low', 120),
        ]
        
        try:
            for achievement_id, title, description, icon, condition, points in achievements:
                cursor.execute('''
                    INSERT OR IGNORE INTO achievements (achievement_id, title, description, icon, unlock_condition, points_reward)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (achievement_id, title, description, icon, condition, points))
                cursor.execute(
                    '''
                    UPDATE achievements
                    SET title = ?, description = ?, icon = ?, unlock_condition = ?, points_reward = ?
                    WHERE achievement_id = ?
                    ''',
                    (title, description, icon, condition, points, achievement_id)
                )
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error initializing achievements: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_achievements(self, user_id: str) -> List[Dict]:
        """Get user's achievements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT
                a.achievement_id,
                a.title,
                a.description,
                a.icon,
                a.points_reward,
                COALESCE(MAX(ua.unlocked), 0) AS unlocked,
                MAX(ua.unlock_date) AS unlock_date
            FROM achievements a
            LEFT JOIN user_achievements ua ON a.achievement_id = ua.achievement_id AND ua.user_id = ?
            GROUP BY a.achievement_id, a.title, a.description, a.icon, a.points_reward
            ORDER BY unlocked DESC, a.title
        ''', (user_id,))
        
        achievements = []
        for row in cursor.fetchall():
            achievements.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'icon': row[3],
                'points': row[4],
                'unlocked': bool(row[5]),
                'date': row[6] if row[6] else None
            })
        
        conn.close()
        return achievements
    
    def unlock_achievement(self, user_id: str, achievement_id: str) -> bool:
        """Unlock an achievement for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if already unlocked
            cursor.execute('''
                SELECT id FROM user_achievements
                WHERE user_id = ? AND achievement_id = ? AND unlocked = 1
            ''', (user_id, achievement_id))
            
            if cursor.fetchone():
                conn.close()
                return False  # Already unlocked
            
            # Get achievement points
            cursor.execute('''
                SELECT points_reward FROM achievements WHERE achievement_id = ?
            ''', (achievement_id,))
            
            result = cursor.fetchone()
            points = result[0] if result else 0
            
            # Unlock achievement
            cursor.execute('''
                UPDATE user_achievements
                SET unlocked = 1, unlock_date = ?
                WHERE user_id = ? AND achievement_id = ?
            ''', (datetime.now(), user_id, achievement_id))
            
            # Add points
            self._add_points(cursor, user_id, points, f"Achievement unlocked: {achievement_id}")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error unlocking achievement: {e}")
            return False
    
    def check_and_unlock_achievements(self, user_id: str) -> List[str]:
        """Check and automatically unlock achievements based on criteria"""
        unlocked = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get latest metrics
            streak_data = self.get_streak_data(user_id)
            metrics = self.get_dashboard_metrics(user_id)
            
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            # Check 7-day streak (Week Warrior)
            if streak_data['current_streak'] >= 7:
                if self.unlock_achievement(user_id, 'week_warrior'):
                    unlocked.append('week_warrior')
            
            # Check wellbeing score >= 80 (Balance Score)
            if metrics['wellbeing_score'] >= 80:
                if self.unlock_achievement(user_id, 'balance_score'):
                    unlocked.append('balance_score')
            
            # Check sleep nights >= 5 (Sleep Champion)
            cursor.execute('''
                SELECT COUNT(*) FROM sleep_data
                WHERE user_id = ? AND date >= ? AND quality_score >= 7
            ''', (user_id, week_ago))
            
            quality_nights = cursor.fetchone()[0]
            if quality_nights >= 5:
                if self.unlock_achievement(user_id, 'sleep_champion'):
                    unlocked.append('sleep_champion')
            
            # Check task completion count (Task Master - 10 tasks completed this week)
            cursor.execute('''
                SELECT COUNT(*) FROM user_tasks
                WHERE user_id = ? AND completed = 1 AND date >= ?
            ''', (user_id, week_ago))
            
            tasks_completed = cursor.fetchone()[0]
            if tasks_completed >= 10:
                if self.unlock_achievement(user_id, 'task_master'):
                    unlocked.append('task_master')
            elif tasks_completed >= 5:
                if self.unlock_achievement(user_id, 'task_starter'):
                    unlocked.append('task_starter')
            
            # Check mood check-ins (Mindful Master - 10 mood check-ins)
            cursor.execute('''
                SELECT COUNT(*) FROM mood_entries
                WHERE user_id = ? AND date >= ?
            ''', (user_id, week_ago))
            
            mood_count = cursor.fetchone()[0]
            if mood_count >= 10:
                if self.unlock_achievement(user_id, 'mindful_master'):
                    unlocked.append('mindful_master')
            elif mood_count >= 5:
                if self.unlock_achievement(user_id, 'mindful_starter'):
                    unlocked.append('mindful_starter')
            
            # Check 3-day streak (Growing Strong)
            if streak_data['current_streak'] >= 3:
                if self.unlock_achievement(user_id, 'growing_strong'):
                    unlocked.append('growing_strong')
            
            # Check screen time reduction (Digital Balance)
            cursor.execute('''
                SELECT AVG(hours), COUNT(*) FROM screen_time
                WHERE user_id = ? AND date >= ?
            ''', (user_id, week_ago))
            
            screen_stats = cursor.fetchone()
            avg_screen = screen_stats[0] or 0
            screen_entry_count = screen_stats[1] or 0
            if screen_entry_count >= 3 and avg_screen < 4:
                if self.unlock_achievement(user_id, 'digital_balance'):
                    unlocked.append('digital_balance')
            
            return unlocked
        except Exception as e:
            print(f"Error checking achievements: {e}")
            return []
        finally:
            conn.close()
    
    def calculate_addiction_risk(self, user_id: str) -> Dict:
        """Calculate addiction risk level based on actual data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            # Get screen time data
            cursor.execute('''
                SELECT AVG(hours), MAX(hours), MIN(hours) FROM screen_time
                WHERE user_id = ? AND date >= ?
            ''', (user_id, week_ago))
            
            screen_time_row = cursor.fetchone()
            avg_screen_time = screen_time_row[0] if screen_time_row[0] else 0
            max_screen_time = screen_time_row[1] if screen_time_row[1] else 0
            
            # Get sleep data
            cursor.execute('''
                SELECT AVG(hours_slept), AVG(quality_score) FROM sleep_data
                WHERE user_id = ? AND date >= ?
            ''', (user_id, week_ago))
            
            sleep_row = cursor.fetchone()
            avg_sleep = sleep_row[0] if sleep_row[0] else 0
            sleep_quality = sleep_row[1] if sleep_row[1] else 0
            
            # Get mood data
            cursor.execute('''
                SELECT AVG(mood_score) FROM mood_entries
                WHERE user_id = ? AND date >= ?
            ''', (user_id, week_ago))
            
            mood_row = cursor.fetchone()
            avg_mood = mood_row[0] if mood_row[0] else 3
            
            # Calculate risk factors
            risk_score = 0
            risk_factors = []
            
            # Screen time risk
            if avg_screen_time > 8:
                risk_score += 40
                risk_factors.append("High screen time (>8 hours/day)")
            elif avg_screen_time > 6:
                risk_score += 20
                risk_factors.append("Elevated screen time (6-8 hours/day)")
            
            # Sleep risk
            if avg_sleep < 5:
                risk_score += 30
                risk_factors.append("Insufficient sleep (<5 hours)")
            elif avg_sleep < 6:
                risk_score += 15
                risk_factors.append("Low sleep (5-6 hours)")
            
            if sleep_quality < 5:
                risk_score += 15
                risk_factors.append("Poor sleep quality")
            
            # Mood risk
            if avg_mood < 2.5:
                risk_score += 15
                risk_factors.append("Low mood/mental health concerns")
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = "Critical"
            elif risk_score >= 60:
                risk_level = "High"
            elif risk_score >= 40:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            conn.close()
            
            return {
                'level': risk_level,
                'score': risk_score,
                'avg_screen_time': round(avg_screen_time, 1),
                'max_screen_time': round(max_screen_time, 1),
                'avg_sleep': round(avg_sleep, 1),
                'avg_mood': round(avg_mood, 1),
                'factors': risk_factors
            }
        except Exception as e:
            conn.close()
            print(f"Error calculating risk: {e}")
            return {
                'level': 'Unknown',
                'score': 0,
                'factors': []
            }
    
    def calculate_goal_progress(self, user_id: str) -> List[Dict]:
        """Calculate progress for all user goals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            goals = []
            
            # Sleep goal
            cursor.execute('''
                SELECT AVG(hours_slept) FROM sleep_data
                WHERE user_id = ? AND date >= ?
            ''', (user_id, week_ago))
            
            sleep_row = cursor.fetchone()
            current_sleep = sleep_row[0] if sleep_row[0] else 0
            progress_sleep = min(100, round((current_sleep / 8) * 100))
            
            goals.append({
                'title': 'Better Sleep',
                'current': round(current_sleep, 1),
                'target': 8,
                'unit': 'hours',
                'progress': progress_sleep,
                'icon': 'fa-moon'
            })
            
            # Screen time goal
            cursor.execute('''
                SELECT AVG(hours) FROM screen_time
                WHERE user_id = ? AND date >= ?
            ''', (user_id, week_ago))
            
            screen_row = cursor.fetchone()
            current_screen = screen_row[0] if screen_row[0] else 0
            progress_screen = max(0, min(100, round(100 - (current_screen / 8) * 100)))
            
            goals.append({
                'title': 'Reduce Screen Time',
                'current': round(current_screen, 1),
                'target': 4,
                'unit': 'hours',
                'progress': progress_screen,
                'icon': 'fa-mobile'
            })
            
            # Social balance goal
            cursor.execute('''
                SELECT COUNT(*) FROM user_tasks
                WHERE user_id = ? AND task_name LIKE '%social%' AND completed = 1 AND date >= ?
            ''', (user_id, week_ago))
            
            social_tasks = cursor.fetchone()[0]
            progress_social = min(100, round((social_tasks / 3) * 100))
            
            goals.append({
                'title': 'Social Balance',
                'current': social_tasks,
                'target': 3,
                'unit': 'interactions',
                'progress': progress_social,
                'icon': 'fa-users'
            })
            
            conn.close()
            return goals
        except Exception as e:
            conn.close()
            print(f"Error calculating goals: {e}")
            return []

# Global database instance
db = DatabaseManager()

# Initialize achievements on startup
db.initialize_achievements()
