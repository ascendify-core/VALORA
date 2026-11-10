# models.py - optional helper (not used directly by main.py now)
import sqlite3
DB_NAME = "smartbudget.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)
