import sqlite3

def reset_transactions():
    conn = sqlite3.connect("budget.db")   # make sure the DB name is correct
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")   # removes all rows
    conn.commit()
    conn.close()
    print("All transactions deleted successfully.")

if __name__ == "__main__":
    reset_transactions()
