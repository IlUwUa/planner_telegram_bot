import sqlite3
import os


DB_FOLDER = "data"
DB_NAME = "tasks.db"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)


def get_connection():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_text TEXT,
            notify_time TEXT
        )
    ''')
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            timezone_name TEXT DEFAULT 'UTC' 
        )
    ''')
    

    conn.commit()
    conn.close()


def add_task(user_id, text, time_str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (user_id, task_text, notify_time) VALUES (?, ?, ?)', 
                   (user_id, text, time_str))
    conn.commit()
    conn.close()


def get_tasks(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, task_text, notify_time FROM tasks WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_task(task_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
    conn.commit()
    is_deleted = cursor.rowcount > 0
    conn.close()
    return is_deleted


def get_due_tasks(current_time_str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, task_text FROM tasks WHERE notify_time = ?", (current_time_str,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_task_by_id(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def set_user_timezone(user_id, tz_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, timezone_name) VALUES (?, ?)', 
                   (user_id, tz_name))
    conn.commit()
    conn.close()


def get_user_timezone(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT timezone_name FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    return 'UTC'