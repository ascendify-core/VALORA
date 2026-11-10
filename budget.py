from database import add_expense, get_expenses, add_budget, get_budget

def record_transaction(username: str, date: str, category: str, amount: float, description: str = "", type_: str = "Expense"):
    add_expense(username, category, amount, date, description, type_)

def fetch_transactions(username: str):
    return get_expenses(username)

def set_budget(username: str, month: str, amount: float):
    add_budget(username, month, amount)

def retrieve_budget(username: str, month: str) -> float:
    return get_budget(username, month)
