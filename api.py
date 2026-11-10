"""
VALORA FastAPI Backend
======================
Drop this file into C:\\Users\\ANAND\\OneDrive\\Desktop\\Prototype
alongside your existing main.py, auth.py, budget.py, database.py etc.

Run with:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload

Find your laptop's local IP:
    Run `ipconfig` in CMD → look for IPv4 Address (e.g. 192.168.1.5)
    Flutter app will connect to http://192.168.1.5:8000
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import datetime

# Import your existing Valora modules (unchanged)
from auth import register_user, validate_user
from budget import retrieve_budget, set_budget, record_transaction, fetch_transactions
from database import (
    init_database,
    get_user,
    update_user_profile,
    add_custom_category,
    list_custom_categories,
    remove_custom_category,
    get_categories_for_user,
)
from professions import get_all_professions, PROFESSIONS, get_categories_for_profession
from predictor import predict_future

# Initialize DB on startup
init_database()

app = FastAPI(
    title="VALORA API",
    description="Backend API for Valora Finance App",
    version="1.0.0"
)

# Allow Flutter app to connect from any IP on your network
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Request / Response Models
# ---------------------------

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    profession: str = "Individual"
    account_type: str = "Individual"

class TransactionRequest(BaseModel):
    username: str
    date: str
    category: str
    amount: float
    note: str = ""
    type: str = "Expense"

class BudgetRequest(BaseModel):
    username: str
    month: str
    amount: float

class CategoryRequest(BaseModel):
    username: str
    profession: str
    category_name: str
    category_type: str = "Expense"

class ProfileUpdateRequest(BaseModel):
    username: str
    profession: str
    account_type: str

# ---------------------------
# Health Check
# ---------------------------

@app.get("/")
def root():
    return {"status": "VALORA API is running 🚀", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------------------
# Auth Routes
# ---------------------------

@app.post("/auth/login")
def login(req: LoginRequest):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    is_valid = validate_user(req.username, req.password)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user = get_user(req.username)
    profession = "Individual"
    account_type = "Individual"
    
    if user:
        _, _, profession, account_type = user
        profession = profession or "Individual"
        account_type = account_type or "Individual"
    
    return {
        "success": True,
        "username": req.username,
        "profession": profession,
        "account_type": account_type,
    }

@app.post("/auth/register")
def register(req: RegisterRequest):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    success = register_user(req.username, req.password, req.profession, req.account_type)
    if not success:
        raise HTTPException(status_code=409, detail="Username already exists")
    
    return {"success": True, "message": "Account created successfully"}

# ---------------------------
# Transaction Routes
# ---------------------------

@app.get("/transactions/{username}")
def get_transactions(username: str):
    transactions = fetch_transactions(username)
    if transactions is None:
        return {"transactions": []}
    return {"transactions": transactions}

@app.post("/transactions")
def add_transaction(req: TransactionRequest):
    try:
        record_transaction(
            req.username,
            req.date,
            req.category,
            req.amount,
            req.note,
            req.type,
        )
        return {"success": True, "message": "Transaction added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------
# Budget Routes
# ---------------------------

@app.get("/budget/{username}")
def get_budget(username: str):
    this_month = datetime.datetime.today().strftime("%B - %Y")
    budget = retrieve_budget(username, this_month)
    return {
        "username": username,
        "month": this_month,
        "budget": budget or 0.0,
    }

@app.get("/budget/{username}/{month}")
def get_budget_by_month(username: str, month: str):
    budget = retrieve_budget(username, month)
    return {
        "username": username,
        "month": month,
        "budget": budget or 0.0,
    }

@app.post("/budget")
def update_budget(req: BudgetRequest):
    try:
        set_budget(req.username, req.month, req.amount)
        return {"success": True, "message": "Budget updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------
# Categories Routes
# ---------------------------

@app.get("/categories/{username}/{profession}")
def get_categories(username: str, profession: str):
    try:
        categories = get_categories_for_user(username, profession, PROFESSIONS)
    except Exception:
        categories = get_categories_for_profession(profession)
    
    return {
        "categories": [
            {"name": name, "type": ctype} for name, ctype in (categories or [])
        ]
    }

@app.post("/categories")
def add_category(req: CategoryRequest):
    added = add_custom_category(
        req.username, req.profession, req.category_name, req.category_type
    )
    if not added:
        raise HTTPException(status_code=409, detail="Category already exists")
    return {"success": True, "message": "Category added"}

@app.delete("/categories/{username}/{profession}/{category_name}")
def delete_category(username: str, profession: str, category_name: str):
    removed = remove_custom_category(username, profession, category_name)
    if not removed:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"success": True, "message": "Category deleted"}

# ---------------------------
# Professions Route
# ---------------------------

@app.get("/professions")
def get_professions():
    return {"professions": get_all_professions()}

# ---------------------------
# Profile Route
# ---------------------------

@app.post("/profile/update")
def update_profile(req: ProfileUpdateRequest):
    success = update_user_profile(req.username, req.profession, req.account_type)
    if not success:
        raise HTTPException(status_code=500, detail="Could not update profile")
    return {"success": True, "message": "Profile updated"}

# ---------------------------
# AI Insights Route
# ---------------------------

@app.get("/insights/{username}")
def get_insights(username: str):
    transactions = fetch_transactions(username)
    
    if not transactions:
        return {
            "has_data": False,
            "message": "Not enough data for insights"
        }
    
    result = predict_future(transactions)
    
    if result is None:
        return {
            "has_data": False,
            "message": "Not enough data for predictions"
        }
    
    # Category predictions
    import pandas as pd
    import datetime

    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    category_predictions = {}
    expense_df = df[df["type"].isin(["Expense", "Savings"])]
    
    if not expense_df.empty:
        total_days = max((df["date"].max() - df["date"].min()).days + 1, 1)
        category_summary = expense_df.groupby("category")["amount"].sum()
        
        for category, amount in category_summary.items():
            daily_avg = amount / total_days
            category_predictions[category] = {
                "weekly": round(daily_avg * 7, 2),
                "monthly": round(daily_avg * 30, 2),
            }

    # Build advice
    advice = []
    if result['monthly'] > 15000:
        advice.append("Reduce dining and entertainment expenses.")
    if result['yearly'] > 250000:
        advice.append("Consider setting stricter budgets to control long-term spending.")
    if not advice:
        advice.append("Your finances look healthy. Keep it up!")
    
    return {
        "has_data": True,
        "predictions": {
            "weekly": result['weekly'],
            "monthly": result['monthly'],
            "yearly": result['yearly'],
        },
        "category_predictions": category_predictions,
        "advice": advice,
    }