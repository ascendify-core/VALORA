"""
professions.py

Built-in profession templates and helpers.
"""

PROFESSIONS = {
    "Individual": {
        "income": ["Salary", "Freelancing", "Investments", "Pension", "Other"],
        "expense": ["Food", "Transport", "Bills", "Rent", "Entertainment", "Healthcare", "Education", "Other"]
    },
    "Farmer": {
        "income": ["Crop Sales", "Government Subsidy", "Pension", "Livestock Sales", "Other"],
        "expense": ["Fertilizers", "Seeds", "Labor", "Irrigation", "Equipment Repair", "Transport", "Bills", "Household"]
    },
    "CEO / Executive": {
        "income": ["Salary", "Bonus", "Stock Options", "Investments", "Other"],
        "expense": ["Household", "Utilities", "Taxes", "Investments", "Travel", "Education", "Dining", "Other"]
    },
    "Banker / Finance Professional": {
        "income": ["Salary", "Bonus", "Investments", "Other"],
        "expense": ["Taxes", "Bills", "Investments", "EMI", "Transport", "Household", "Other"]
    },
    "Student": {
        "income": ["Allowance", "Scholarship", "Part-time Work", "Other"],
        "expense": ["Tuition", "Books", "Food", "Transport", "Leisure", "Other"]
    },
    "Freelancer": {
        "income": ["Client Payments", "Royalties", "Investments", "Other"],
        "expense": ["Internet", "Software", "Equipment", "Taxes", "Transport", "Household", "Other"]
    },
    "Homemaker": {
        "income": ["Family Support", "Pension", "Other"],
        "expense": ["Groceries", "Utilities", "Household Supplies", "Healthcare", "Education", "Other"]
    },
    "Business Owner": {
        "income": ["Sales Revenue", "Service Income", "Other"],
        "expense": ["Raw Materials", "Salaries", "Rent", "Utilities", "Marketing", "Other"]
    },
    "Teacher": {
        "income": ["Salary", "Tuition Classes", "Other"],
        "expense": ["Books", "Transport", "Household", "Other"]
    },
    "Doctor": {
        "income": ["Consultation Fees", "Hospital Salary", "Other"],
        "expense": ["Clinic Rent", "Equipment", "Insurance", "Other"]
    }
}

def get_all_professions():
    return sorted(PROFESSIONS.keys())

def get_categories_for_profession(profession: str):
    prof = PROFESSIONS.get(profession, PROFESSIONS["Individual"])
    income = prof.get("income", [])
    expense = prof.get("expense", [])
    categories = [ (c, "Income") for c in income ] + [ (c, "Expense") for c in expense ]
    seen = set()
    out = []
    for name, typ in categories:
        if name not in seen:
            out.append((name, typ))
            seen.add(name)
    return out

def add_custom_profession(name: str, income_list: list = None, expense_list: list = None):
    if income_list is None:
        income_list = []
    if expense_list is None:
        expense_list = []
    PROFESSIONS[name] = {
        "income": income_list,
        "expense": expense_list
    }
