import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
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
    conn.commit()

def get_phone_number(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT phone_number FROM users WHERE user_id =?', (user_id,))
    phone_number = cursor.fetchone()
    conn.close()
    return phone_number[0] if phone_number else None

def get_program(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT program FROM users WHERE user_id =?', (user_id,))
    program = cursor.fetchone()
    conn.close()
    return program[0] if program else None
    
def save_user_program(user_id, program):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO users (user_id, program)
    VALUES (?, ?)
    ''', (user_id, program))
    conn.commit()

def save_user_contact(user_id, phone_number, first_name, username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE users
    SET phone_number = ?, first_name = ?, username = ?
    WHERE user_id = ?
    ''', (phone_number, first_name, username, user_id))
    conn.commit()

def get_user_data(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data