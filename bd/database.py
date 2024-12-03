import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Tuple, Any
import logging
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = 'users.db'
CACHE_TIMEOUT = 300  # 5 minutes

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable row factory for named columns
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def init_db():
    """Initialize database tables"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    phone_number TEXT,
                    first_name TEXT,
                    program TEXT,
                    username TEXT
                )
            ''')

            # Create questions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT,
                    message_id INTEGER UNIQUE NOT NULL
                )
            ''')

            # Add indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_user_id ON questions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_message_id ON questions(message_id)')

            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise


def save_question(user_id: int, question: str, message_id: int) -> bool:
    """Save a new question to the database with message_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO questions (user_id, question, message_id)
                VALUES (?, ?, ?)
            ''', (user_id, question, message_id))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error saving question: {e}")
        return False

def get_question_and_username_by_message_id(message_id: int) -> Optional[Tuple[str, str]]:
    """Get the question text and username by message_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT q.question, u.username
                FROM questions q
                JOIN users u ON q.user_id = u.user_id
                WHERE q.message_id = ?
            ''', (message_id,))
            result = cursor.fetchone()
            return (result[0], result[1]) if result else (None, None)
    except sqlite3.Error as e:
        logger.error(f"Error fetching question and username: {e}")
        return None, None

@lru_cache(maxsize=100)
def get_unanswered_questions() -> List[Tuple]:
    """Get all unanswered questions with caching"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM questions WHERE answer IS NULL')
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error fetching unanswered questions: {e}")
        return []

def get_question_by_message_id(message_id: int) -> Optional[str]:
    """Get the question text by message_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT question FROM questions WHERE message_id = ?', (message_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Error fetching question: {e}")
        return None

def get_user_id_by_question_id(message_id: int) -> Optional[int]:
    """Get user_id associated with a question by message_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM questions WHERE message_id = ?', (message_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Error fetching user_id for question: {e}")
        return None
def save_answer(question_id: int, answer: str) -> bool:
    """Save an answer to a question"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE questions
                SET answer = ?
                WHERE message_id = ?
            ''', (answer, question_id))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error saving answer: {e}")
        return False

def add_user_if_not_exists(user_id: int) -> bool:
    """Add a new user if they don't exist"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error adding user: {e}")
        return False

@lru_cache(maxsize=100)
def get_phone_number(user_id: int) -> Optional[str]:
    """Get user's phone number with caching"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT phone_number FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Error fetching phone number: {e}")
        return None

@lru_cache(maxsize=100)
def get_program(user_id: int) -> Optional[str]:
    """Get user's program with caching"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT program FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Error fetching program: {e}")
        return None

def save_user_program(user_id: int, program: str) -> bool:
    """Save or update user's program"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, program)
                VALUES (?, ?)
            ''', (user_id, program))
            conn.commit()
            get_program.cache_clear()  # Clear the cache for this user
            return True
    except sqlite3.Error as e:
        logger.error(f"Error saving user program: {e}")
        return False

def save_user_contact(user_id: int, phone_number: str, first_name: str, username: str) -> bool:
    """Save or update user contact information"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users
                SET phone_number = ?, first_name = ?, username = ?
                WHERE user_id = ?
            ''', (phone_number, first_name, username, user_id))
            conn.commit()
            get_phone_number.cache_clear()  # Clear the cache for this user
            return True
    except sqlite3.Error as e:
        logger.error(f"Error saving user contact: {e}")
        return False

@lru_cache(maxsize=100)
def get_user_data(user_id: int) -> Optional[Tuple[Any, ...]]:
    """Get all user data with caching"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Error fetching user data: {e}")
        return None
