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

            # Create tickets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create ticket_messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticket_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    message_id INTEGER UNIQUE NOT NULL,
                    question TEXT,
                    answer TEXT,
                    answer_created_at TIMESTAMP,
                    admin_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Add indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket_id ON ticket_messages(ticket_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticket_messages_message_id ON ticket_messages(message_id)')


            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise

def save_question(user_id: int, question: str, message_id: int, ticket_id: int) -> bool:
    """Save a new question to the database with message_id and ticket_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ticket_messages (user_id, message, message_id, question, ticket_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, question, message_id, question, ticket_id))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error saving question: {e}")
        return False

def save_ticket_message(ticket_id: int, user_id: int, message: str, message_id: int, is_question: bool = False) -> bool:
    """Save a message to a ticket"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if is_question:
                cursor.execute('''
                    INSERT INTO ticket_messages (ticket_id, user_id, message, message_id, question)
                    VALUES (?, ?, ?, ?, ?)
                ''', (ticket_id, user_id, message, message_id, message))
            else:
                cursor.execute('''
                    INSERT INTO ticket_messages (ticket_id, user_id, message, message_id)
                    VALUES (?, ?, ?, ?)
                ''', (ticket_id, user_id, message, message_id))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error saving ticket message: {e}")
        return False

def get_question_and_username_by_message_id(message_id: int) -> Optional[Tuple[str, str]]:
    """Get the question text and username by message_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tm.question, u.username
                FROM ticket_messages tm
                JOIN users u ON tm.user_id = u.user_id
                WHERE tm.message_id = ?
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
            cursor.execute('SELECT * FROM ticket_messages WHERE answer IS NULL')
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error fetching unanswered questions: {e}")
        return []

def get_question_by_message_id(message_id: int) -> Optional[str]:
    """Get the question text by message_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT question FROM ticket_messages WHERE message_id = ?', (message_id,))
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
            cursor.execute('SELECT user_id FROM ticket_messages WHERE message_id = ?', (message_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Error fetching user_id for question: {e}")
        return None

def save_answer(question_id: int, answer: str, admin_id: int) -> bool:
    """Save an answer to a question"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE ticket_messages
                SET answer = ?, answer_created_at = CURRENT_TIMESTAMP, admin_id = ?
                WHERE message_id = ?
            ''', (answer, admin_id, question_id))
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

def create_ticket(user_id: int) -> int:
    """Create a new ticket for a user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tickets (user_id)
                VALUES (?)
            ''', (user_id,))
            ticket_id = cursor.lastrowid
            conn.commit()
            return ticket_id
    except sqlite3.Error as e:
        logger.error(f"Error creating ticket: {e}")
        return None

def get_ticket_messages(ticket_id: int) -> List[Tuple]:
    """Get all messages for a ticket"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ticket_messages WHERE ticket_id = ?', (ticket_id,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error fetching ticket messages: {e}")
        return []

def close_ticket(ticket_id: int) -> bool:
    """Close a ticket"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tickets
                SET status = 'closed'
                WHERE id = ?
            ''', (ticket_id,))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error closing ticket: {e}")
        return False

def get_ticket_history(ticket_id: int) -> List[Tuple]:
    """Get the history of a ticket, including the initial question and all subsequent messages"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tm.message, tm.created_at, u.username, tm.answer, tm.answer_created_at, a.username AS admin_username
                FROM ticket_messages tm
                JOIN users u ON tm.user_id = u.user_id
                LEFT JOIN users a ON tm.admin_id = a.user_id
                WHERE tm.ticket_id = ?
                ORDER BY tm.created_at
            ''', (ticket_id,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error fetching ticket history: {e}")
        return []

def get_user_id_by_ticket_id(ticket_id: int) -> Optional[int]:
    """Get user_id associated with a ticket by ticket_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM tickets WHERE id = ?', (ticket_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Error fetching user_id for ticket: {e}")
        return None

def get_user_id_by_ticket_message_id(message_id: int) -> Optional[int]:
    """Get user_id associated with a ticket message by message_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM ticket_messages WHERE message_id = ?', (message_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Error fetching user_id for ticket message: {e}")
        return None

def get_ticket_id_by_message_id(message_id: int) -> Optional[int]:
    """Get ticket_id associated with a message by message_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT ticket_id FROM ticket_messages WHERE message_id = ?', (message_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Error fetching ticket_id for message: {e}")
        return None

def get_username_by_user_id(user_id: int) -> Optional[str]:
    """Get username associated with a user by user_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Error fetching username for user: {e}")
        return None

def is_ticket_open(ticket_id: int) -> bool:
    """Check if a ticket is open"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT status FROM tickets WHERE id = ?', (ticket_id,))
            result = cursor.fetchone()
            return result[0] == 'open' if result else False
    except sqlite3.Error as e:
        logger.error(f"Error checking ticket status: {e}")
        return False