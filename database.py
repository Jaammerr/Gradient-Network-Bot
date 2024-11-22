import sqlite3

conn = sqlite3.connect('database.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def init_db():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        username TEXT,
        created_date TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS captcha (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        service TEXT,
        api_key TEXT,
        status BOOLEAN
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        email TEXT,
        password TEXT,
        imap_pass TEXT,
        client_id TEXT,
        node_password TEXT,  
        points INTEGER DEFAULT 0,
        uid TEXT,
        referral_code TEXT,
        referrer TEXT,
        referrals INTEGER,
        nodes INTEGER,
        is_verified BOOLEAN,   
        FOREIGN KEY(user_id) REFERENCES users(telegram_id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS proxies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        proxy TEXT,
        FOREIGN KEY(user_id) REFERENCES users(telegram_id)
    )''')

    conn.commit()

def add_user(telegram_id, username, created_date):
    cursor.execute('INSERT OR IGNORE INTO users (telegram_id, username, created_date) VALUES (?, ?, ?)', (telegram_id, username, created_date))
    conn.commit()

def add_accounts_to_user(user_id, accounts):
    for email, password, imap_pass in accounts:
        cursor.execute('INSERT INTO accounts (user_id, email, password, imap_pass) VALUES (?, ?, ?, ?)', (user_id, email, password, imap_pass))
    conn.commit()

def add_captcha_to_user(user_id, service, api_key, status):
    cursor.execute('INSERT INTO captcha (user_id, service, api_key, status) VALUES (?, ?, ?, ?)', (user_id, service, api_key, status))
    conn.commit()

def add_proxies_to_user(user_id, proxies):
    for proxy in proxies:
        cursor.execute('INSERT INTO proxies (user_id, proxy) VALUES (?, ?)', (user_id, proxy))
    conn.commit()

def get_user(telegram_id):
    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    return cursor.fetchone()

def get_user_accounts(user_id):
    cursor.execute('SELECT id, user_id, email, password, imap_pass, client_id, node_password, is_verified FROM accounts WHERE user_id = ? AND (is_verified IS NULL OR is_verified != 0)', (user_id,))
    return cursor.fetchall()

def get_user_accounts_for_register(user_id):
    cursor.execute('SELECT id, user_id, email, password, imap_pass, client_id, node_password, is_verified FROM accounts WHERE user_id = ? AND (is_verified IS NULL OR is_verified != 1)', (user_id,))
    return cursor.fetchall()

def get_user_accounts_stats(user_id):
    cursor.execute('SELECT id, uid, email, is_verified, points, referral_code, referrer, referrals, nodes FROM accounts WHERE user_id = ?', (user_id,))
    return cursor.fetchall()

def get_user_proxies(user_id):
    cursor.execute('SELECT proxy FROM proxies WHERE user_id = ?', (user_id,))
    return [row['proxy'] for row in cursor.fetchall()]

def get_user_captcha_service_and_key(user_id, service: str = None, status: bool = True):
    if service:
        cursor.execute('SELECT service, api_key, status FROM captcha WHERE user_id = ? AND service = ?', (user_id, service))
    else:
        cursor.execute('SELECT service, api_key, status FROM captcha WHERE user_id = ? AND status = ?', (user_id, status))

    result = cursor.fetchone()
    return result
    
def get_user_captcha_service_and_key_stats(user_id):
    cursor.execute('SELECT service, api_key, status FROM captcha WHERE user_id = ?', (user_id,))
    result = cursor.fetchall()
    return result

def get_user_accounts_count(user_id):
    cursor.execute('SELECT COUNT(*) FROM accounts WHERE user_id = ?', (user_id,))
    return cursor.fetchone()[0]

def get_user_verified_accounts_count(user_id):
    cursor.execute('SELECT COUNT(*) FROM accounts WHERE user_id = ? AND is_verified = ?', (user_id, True))
    return cursor.fetchone()[0]

def get_user_proxies_count(user_id):
    cursor.execute('SELECT COUNT(*) FROM proxies WHERE user_id = ?', (user_id,))
    return cursor.fetchone()[0]

def get_total_points(user_id):
    cursor.execute('''
        SELECT SUM(points)
        FROM (
            SELECT DISTINCT email, MAX(points) AS points
            FROM accounts
            WHERE user_id = ?
            GROUP BY email
        ) AS unique_accounts
    ''', (user_id,))
    result = cursor.fetchone()[0]
    return result if result is not None else 0

def update_account_points(user_id, email, points):
    cursor.execute('UPDATE accounts SET points = ? WHERE user_id = ? AND email = ?', (points, user_id, email))

    conn.commit()

def update_account_sentry_node(user_id, email, client_id, node_password):
    cursor.execute('UPDATE accounts SET client_id = ?, node_password = ? WHERE id = (SELECT id FROM accounts WHERE user_id = ? AND email = ? AND client_id IS NULL AND node_password IS NULL LIMIT 1)', (client_id, node_password, user_id, email))

    conn.commit()

def update_user_captcha_key(user_id, api_key, service):
    cursor.execute('UPDATE captcha SET api_key = ? WHERE user_id = ? AND service = ?', (api_key, user_id, service))
    conn.commit()

def update_user_captcha_status(user_id, status, service):
    cursor.execute('UPDATE captcha SET status = ? WHERE user_id = ? AND service = ?', (status, user_id, service))
    conn.commit()

def update_account_verified_status(status, user_id, email):
    cursor.execute('UPDATE accounts SET is_verified = ? WHERE user_id = ? AND email = ?', (status, user_id, email))
    conn.commit()

def update_account_statistics(uid, points, referral_code, referrer, referrals, nodes, user_id, email):
    cursor.execute('UPDATE accounts SET uid = ?, points = ?, referral_code = ?, referrer = ?, referrals = ?, nodes = ? WHERE user_id = ? AND email = ?', (uid, points, referral_code, referrer, referrals, nodes, user_id, email))
    conn.commit()

def delete_user_accounts(user_id):
    cursor.execute('DELETE FROM accounts WHERE user_id = ?', (user_id,))
    conn.commit()

def delete_user_proxies(user_id):
    cursor.execute('DELETE FROM proxies WHERE user_id = ?', (user_id,))
    conn.commit()