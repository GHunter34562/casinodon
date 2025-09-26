import sqlite3
import logging

DB_NAME = 'bot.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0.0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            user_id INTEGER,
            amount_usd REAL,
            expected_amount REAL,
            paid BOOLEAN DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER,
            stake REAL,
            chat_id INTEGER,
            message_id INTEGER
        )
    ''')
    # Проверим, есть ли столбец message_id, и если нет — добавим его
    cursor.execute("PRAGMA table_info(active_games)")
    columns = [info[1] for info in cursor.fetchall()]
    if "message_id" not in columns:
        cursor.execute("ALTER TABLE active_games ADD COLUMN message_id INTEGER")
    conn.commit()
    conn.close()

def ensure_user_exists(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0.0)', (user_id,))
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0

def add_user_balance(user_id, amount):
    ensure_user_exists(user_id)  # Убедимся, что пользователь есть в базе
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def set_user_balance(user_id, amount):
    ensure_user_exists(user_id)  # Убедимся, что пользователь есть в базе
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def remove_user_balance(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    balance = cursor.fetchone()
    if balance and balance[0] >= amount:
        cursor.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def get_all_users(limit=10, offset=0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, balance FROM users ORDER BY user_id LIMIT ? OFFSET ?', (limit, offset))
    result = cursor.fetchall()
    conn.close()
    return result

def get_users_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    result = cursor.fetchone()
    conn.close()
    return result[0]

def save_payment(payment_id, user_id, amount_usd, expected_amount):
    ensure_user_exists(user_id)  # Убедимся, что пользователь есть в базе
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO payments (payment_id, user_id, amount_usd, expected_amount, paid)
        VALUES (?, ?, ?, ?, 0)
    ''', (payment_id, user_id, amount_usd, expected_amount))
    conn.commit()
    conn.close()

def update_payment_status(payment_id, paid):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE payments SET paid = ? WHERE payment_id = ?', (paid, payment_id))
    conn.commit()
    conn.close()

def get_payment_status(payment_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT paid FROM payments WHERE payment_id = ?', (payment_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else False

def create_active_game(user1_id, stake, chat_id, message_id):
    ensure_user_exists(user1_id)  # Убедимся, что пользователь есть в базе
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO active_games (user1_id, stake, chat_id, message_id) VALUES (?, ?, ?, ?)', (user1_id, stake, chat_id, message_id))
    conn.commit()
    conn.close()

def get_active_game_by_stake_and_msg(stake, chat_id, user2_id, msg_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user1_id FROM active_games WHERE stake = ? AND chat_id = ? AND user1_id != ? AND message_id = ?', (stake, chat_id, user2_id, msg_id))
    result = cursor.fetchone()
    if result:
        user1_id = result[0]
        cursor.execute('DELETE FROM active_games WHERE user1_id = ? AND stake = ? AND chat_id = ? AND message_id = ?', (user1_id, stake, chat_id, msg_id))
        conn.commit()
    conn.close()
    return result[0] if result else None

def delete_active_game_by_message_id(msg_id, chat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM active_games WHERE message_id = ? AND chat_id = ?', (msg_id, chat_id))
    conn.commit()
    conn.close()

def get_game_creator_by_message_id(msg_id, chat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user1_id FROM active_games WHERE message_id = ? AND chat_id = ?', (msg_id, chat_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_active_game_by_stake(stake, chat_id, user2_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user1_id, message_id FROM active_games WHERE stake = ? AND chat_id = ? AND user1_id != ?', (stake, chat_id, user2_id))
    result = cursor.fetchone()
    if result:
        user1_id, msg_id = result
        cursor.execute('DELETE FROM active_games WHERE user1_id = ? AND stake = ? AND chat_id = ?', (user1_id, stake, chat_id))
        conn.commit()
    conn.close()
    return result[0] if result else None