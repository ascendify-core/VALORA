import sqlite3
from typing import Optional, List, Tuple, Dict

DB_NAME = "smartbudget.db"

def init_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            profession TEXT DEFAULT 'Individual',
            account_type TEXT DEFAULT 'Individual'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            username TEXT,
            month TEXT,
            amount REAL,
            PRIMARY KEY (username, month)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            category TEXT,
            type TEXT,
            amount REAL,
            date TEXT,
            description TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS custom_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            profession TEXT,
            category TEXT,
            type TEXT
        )
    """)

    conn.commit()
    conn.close()

# ---------------- USER FUNCTIONS ----------------
def add_user(username, password, profession, account_type):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?)",
            (username, password, profession, account_type)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    result = cur.fetchone()
    conn.close()
    return result

def update_user_profile(username, profession, account_type):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET profession=?, account_type=? WHERE username=?", (profession, account_type, username))
    conn.commit()
    ok = cur.rowcount > 0
    conn.close()
    return ok

# ---------------- BUDGET ----------------
def add_budget(username, month, amount):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO budgets VALUES (?, ?, ?)", (username, month, amount))
    conn.commit()
    conn.close()

def get_budget(username, month):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT amount FROM budgets WHERE username=? AND month=?", (username, month))
    res = cur.fetchone()
    conn.close()
    return float(res[0]) if res else 0.0

# ---------------- TRANSACTIONS ----------------
def add_expense(username, category, amount, date, description, type_):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (username, category, type, amount, date, description) VALUES (?, ?, ?, ?, ?, ?)",
        (username, category, type_, amount, date, description)
    )
    conn.commit()
    conn.close()

def get_expenses(username):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT category, type, amount, date, description FROM transactions WHERE username=? ORDER BY date DESC",
        (username,)
    )
    rows = cur.fetchall()
    conn.close()

    tx_list = []
    for row in rows:
        tx_list.append({
            "category": row[0],
            "type": row[1],
            "amount": float(row[2]),
            "date": row[3],
            "description": row[4]
        })
    return tx_list

# ---------------- CUSTOM CATEGORIES ----------------
def add_custom_category(username, profession, category, type_):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO custom_categories (username, profession, category, type) VALUES (?, ?, ?, ?)",
        (username, profession, category, type_)
    )
    conn.commit()
    conn.close()

def remove_custom_category(username, profession, category):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM custom_categories WHERE username=? AND profession=? AND category=?",
        (username, profession, category)
    )
    conn.commit()
    conn.close()

def list_custom_categories(username, profession):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, category, type FROM custom_categories WHERE username=? AND profession=?",
        (username, profession)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_categories_for_user(username, profession, professions_templates):
    base_prof = professions_templates.get(profession, professions_templates["Individual"])
    combined = []

    for c in base_prof["income"]:
        combined.append((c, "Income"))
    for c in base_prof["expense"]:
        combined.append((c, "Expense"))

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT category, type FROM custom_categories WHERE username=? AND profession=?",
        (username, profession)
    )
    rows = cur.fetchall()
    conn.close()

    for cat, typ in rows:
        combined.append((cat, typ))

    return combined
