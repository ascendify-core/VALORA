import sqlite3
DB_NAME = "smartbudget.db"

def add_reminder(username: str, title: str, due_date: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO reminders (username, title, due_date) VALUES (?, ?, ?)", (username, title, due_date))
    conn.commit()
    conn.close()

def get_reminders(username: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT title, due_date FROM reminders WHERE username=? ORDER BY due_date ASC", (username,))
    results = cur.fetchall()
    conn.close()
    return results

def get_due_reminders(username: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT title, due_date FROM reminders WHERE username=? AND due_date <= DATE('now') ORDER BY due_date ASC", (username,))
    results = cur.fetchall()
    conn.close()
    return results
