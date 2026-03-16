import sqlite3
from aiogram import Dispatcher, types
conn = sqlite3.connect("bot.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        balance REAL DEFAULT 1000,
        rating INTEGER DEFAULT 0,
        league TEXT DEFAULT 'bronze',
        btc_balance REAL DEFAULT 0,
        eth_balance REAL DEFAULT 0,
        ai_requests_today INTEGER DEFAULT 0,
        last_request_date DATE DEFAULT CURRENT_DATE
    )
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_states (
        user_id INTEGER PRIMARY KEY,
        action TEXT,
        coin TEXT,
        amount REAL,
        step TEXT
    )
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS ai_stats (
        id INTEGER PRIMARY KEY,
        date DATE DEFAULT CURRENT_DATE,
        total_requests INTEGER DEFAULT 0
    )
''')
conn.commit()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS ai_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,    
        answer TEXT NOT NULL,  
        model TEXT,
        created_at DATE DEFAULT CURRENT_DATE
    )  
''')


cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]
if 'btc_balance' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN btc_balance REAL DEFAULT 0")

if 'eth_balance' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN eth_balance REAL DEFAULT 0")

conn.commit()



async def get_user_profile(user_id):
    cursor.execute(
        "SELECT balance, rating, league, btc_balance, eth_balance "
        "FROM users "
        "WHERE id = ?",
        (user_id,)
    )
    user = cursor.fetchone()

    if user is None:
        return None
    else:
        balance = user[0]
        rating = user[1]
        league = user[2]
        btc_balance = user[3]
        eth_balance = user[4]
        return {
            "balance": balance,
            "rating": rating,
            "league": league,
            "btc_balance": btc_balance,
            "eth_balance": eth_balance,
        }


async def get_top_users(limit=10):
    cursor.execute(
        "SELECT id, balance FROM users ORDER BY balance DESC LIMIT ?",
        (limit,)
    )
    users = cursor.fetchall()
    return users






