# main.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import datetime
import numpy as np

from streamlit_option_menu import option_menu
from auth import register_user, validate_user
from budget import retrieve_budget, set_budget, record_transaction, fetch_transactions
from predictor import predict_future
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

# Initialize DB (safe if called repeatedly)
init_database()

# ---------------------------
# Session defaults
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "profession" not in st.session_state:
    st.session_state.profession = "Individual"
if "account_type" not in st.session_state:
    st.session_state.account_type = "Individual"
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "username_input" not in st.session_state:
    st.session_state.username_input = ""
if "password_input" not in st.session_state:
    st.session_state.password_input = ""

# ---------------------------
# UI theme (minimal white-purple)
# ---------------------------
st.set_page_config(page_title="VALORA", page_icon="💰", layout="wide")


st.markdown(
"""
<link href='https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap' rel='stylesheet'>

<style>

body {
    background-color:#ffffff;
    font-family:'Poppins',sans-serif;
    color:#240046;
}

/* Remove sidebar rectangle */
section[data-testid="stSidebar"] {
    background: transparent;
}

section[data-testid="stSidebar"] > div {
    background: transparent;
    border: none;
}

/* Menu items */
.nav-link {
    font-size:16px;
    font-weight:600;
    color:#5a189a;
    border-radius:10px;
    margin-bottom:6px;
}

/* Hover effect */
.nav-link:hover {
    background:#f3e8ff;
    color:#240046;
}

/* Selected menu item */
.nav-link-selected {
    background: linear-gradient(90deg,#cdb8ff,#a88df2);
    color:white !important;
    border-radius:10px;
}

/* Buttons */
.stButton>button {
    background:#cdb8ff;
    border:none;
    border-radius:8px;
    padding:8px 18px;
    font-weight:600;
    color:#240046;
}

.stButton>button:hover {
    background:#a88df2;
    color:white;
}

/* Dashboard cards */
.card {
    background:#ffffff;
    border-radius:12px;
    padding:14px;
    text-align:center;
    box-shadow:0 6px 18px rgba(93,33,112,0.06);
}

.metric-title {
    font-size:0.95rem;
    color:#6a00a8;
}

.metric-value {
    font-size:1.5rem;
    color:#240046;
    font-weight:700;
}

</style>
""",
unsafe_allow_html=True,
)

# ---------------------------
# Auth pages
# ---------------------------
# ---------------------------
# LOGIN PAGE (improved with Enter support)
# ---------------------------
def login_page():
    st.markdown("""
    <div style="
        max-width:800px;
        margin:80px auto;
        padding:40px;
        background: linear-gradient(145deg, #1f1f27, #2c2c34);
        border-radius:16px;
        box-shadow:0 8px 24px rgba(0,0,0,0.5);
        color:white;
        font-family: 'Poppins', sans-serif;
    ">
        <h1 style='text-align:center; color:#8A2BE2;'>💰 VALORA LOGIN</h1>
        <p style='text-align:center; color:#ccc; font-size:0.9rem;'>Track your finances safely</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        with st.form("login_form"):
            st.session_state.username_input = st.text_input(
                "Username", 
                placeholder="Enter your username",
                value=st.session_state.username_input
            )
            st.session_state.password_input = st.text_input(
                "Password", 
                type="password", 
                placeholder="Enter your password",
                value=st.session_state.password_input
            )
            login_btn = st.form_submit_button("Login")

            if login_btn:
                if validate_user(st.session_state.username_input, st.session_state.password_input):
                    st.session_state.logged_in = True
                    st.session_state.username = st.session_state.username_input

                    user = get_user(st.session_state.username)
                    if user:
                        _, _, profession, account_type = user
                        st.session_state.profession = profession or "Individual"
                        st.session_state.account_type = account_type or "Individual"
                else:
                    st.error("Invalid username or password")

        if st.button("Create an account"):
            st.session_state.show_signup = True
            st.rerun()

def signup_page():
    st.title("Create VALORA Account")

    username = st.text_input("Create Username")
    password = st.text_input("Create Password", type="password")

    professions = get_all_professions()

    profession = st.selectbox(
        "Profession",
        professions,
        index=professions.index("Individual") if "Individual" in professions else 0
    )

    account_type = st.selectbox("Account Type", ["Individual", "Family"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sign Up", key="signup_btn"):
            if not username or not password:
                st.error("Please enter username and password.")
            else:
                success = register_user(username, password, profession, account_type)

                if success:
                    st.success("Account created successfully! Please login.")
                    st.session_state.show_signup = False
                    st.rerun()
                else:
                    st.error("Username already exists")

    with col2:
        if st.button("Back to Login", key="back_login_btn"):
            st.session_state.show_signup = False
            st.rerun()


if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
    st.stop()

# ---------------------------
# Sidebar navigation
# ---------------------------

with st.sidebar:
    menu = option_menu(
        "💰 VALORA",
        [
            "🏠 Dashboard",
            "➕ Add Transaction",
            "📊 Analytics",
            "💰 Budget Planner",
            "🧰 Categories",
            "🤖 AI Insights",
            "⚙️ Settings",
        ],
        icons=[
            "house",
            "plus-circle",
            "bar-chart",
            "wallet",
            "tools",
            "gear"
        ],
        menu_icon="cash-stack",
        default_index=0,
    )

# ---------------------------
# Helpers
# ---------------------------
def get_user_transactions_df():
    tx = fetch_transactions(st.session_state.username)
    if not tx:
        return pd.DataFrame()
    df = pd.DataFrame(tx)
    # Normalize column names & types
    if "date" in df.columns:
        df["Date"] = pd.to_datetime(df["date"], errors="coerce")
    elif "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    else:
        df["Date"] = pd.to_datetime(pd.Series(df.get("date", [])), errors="coerce")
    # Ensure amount numeric
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["type"] = df["type"].fillna("Expense")
    df["category"] = df["category"].fillna("Other")
    df["Month"] = df["Date"].dt.strftime("%B - %Y").fillna("Unknown")
    return df


# ---------------------------
# PAGES
# ---------------------------

# --- DASHBOARD ---
if menu == "🏠 Dashboard":
    st.markdown(
    f"""
    <div style="
        background: linear-gradient(90deg,#a88df2,#cdb8ff);
        padding:25px;
        border-radius:15px;
        color:white;
        text-align:center;
        font-size:26px;
        font-weight:600;
        margin-bottom:20px;
    ">
        Welcome back, {st.session_state.username} 👋
        <br>
        <span style="font-size:16px;font-weight:400;">
        Here's your financial overview
        </span>
    </div>
    """,
    unsafe_allow_html=True
)
    st.subheader("Here is your financial overview")
    df = get_user_transactions_df()

    if df.empty:
        st.info("No transactions yet. Add one from ➕ Add Transaction.")
    else:
        # choose month
        months = sorted(df["Month"].unique(), key=lambda x: datetime.datetime.strptime(x, "%B - %Y"))
        selected_month = st.selectbox("Select Month", months)
        filtered = df[df["Month"] == selected_month]

        # safe aggregations with defaults
        total_income = float(filtered.loc[filtered["type"] == "Income", "amount"].sum()) if not filtered.empty else 0.0
        total_expense = float(filtered.loc[filtered["type"] == "Expense", "amount"].sum()) if not filtered.empty else 0.0
        total_savings = float(filtered.loc[filtered["type"] == "Savings", "amount"].sum()) if not filtered.empty else 0.0

        # balance: income minus (expense + savings)
        balance = total_income - (total_expense + total_savings)

        c1, c2, c3, c4 = st.columns(4)

        cards = [
            ("💰 Income", total_income, "#7f53ac", "#647dee"),       # muted purple → soft blue
            ("💸 Expenses", total_expense, "#ff758c", "#ff7eb3"),    # soft pink → pastel rose
            ("🏦 Savings", total_savings, "#6dd5ed", "#2193b0"),     # pastel cyan → muted blue
            ("📊 Balance", balance, "#fbc2eb", "#a6c1ee"),
        ]

        # Add CSS for hover effect once
        st.markdown("""
        <style>
        .kpi-card {
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            color: #240046;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
            cursor: default;
        }
        .kpi-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 12px 25px rgba(0,0,0,0.25);
        }
        .kpi-card h4 {
            margin-bottom: 5px;
            font-weight: 600;
        }
        .kpi-card h2 {
            margin-top: 0;
            font-weight: 700;
        }
        </style>
        """, unsafe_allow_html=True)

        # Render cards
        for col, (title, value, grad_start, grad_end) in zip([c1, c2, c3, c4], cards):
            col.markdown(f"""
            <div class='kpi-card' style='background: linear-gradient(135deg, {grad_start}, {grad_end});'>
                <h4>{title}</h4>
                <h2>₹{value:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        this_month = datetime.datetime.today().strftime("%B - %Y")
        budget = retrieve_budget(st.session_state.username, this_month)

        if budget:
            if total_expense > budget:
                st.error(f"Budget exceeded by ₹{total_expense - budget:.2f}")
            else:
                st.success(f"Remaining Budget: ₹{budget - total_expense:.2f}")
        else:
            st.warning("No budget set for this month.")

        if budget:
            progress = min(total_expense / budget, 1.0)
            st.markdown("### Budget Usage")
            st.progress(progress)
            st.write(f"₹{total_expense:.2f} / ₹{budget:.2f} used")

        st.download_button("Download CSV", filtered.to_csv(index=False), "SmartBudget.csv", "text/csv")

        #Recent Transanction
        st.markdown("### Recent Transactions")

        recent_tx = filtered.sort_values("Date", ascending=False).head(10)

        st.dataframe(
    recent_tx[["Date", "category", "type", "amount"]],
    use_container_width=True,
    height=350
)

# --- ADD TRANSACTION ---
elif menu == "➕ Add Transaction":
    st.subheader("Add a New Transaction")

    # prepare categories: built-in + user custom
    try:
        categories = get_categories_for_user(st.session_state.username, st.session_state.profession, PROFESSIONS)
    except Exception:
        categories = get_categories_for_profession(st.session_state.profession)
    cat_names = [c for c, _ in categories] if categories else ["Other"]

    with st.form("tx_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.date.today())
            category = st.selectbox("Category", cat_names)
        with col2:
            amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
            # auto-detect type but allow override
            inferred_type = "Expense"
            for cname, ctype in categories:
                if cname == category:
                    inferred_type = ctype
                    break
            type_choice = st.radio("Type", ["Income", "Expense", "Savings"], index=0)
            # map selection to final type
            final_type = type_choice

        note = st.text_input("Note (optional)")
        submitted = st.form_submit_button("Add Transaction")
        if submitted:
            # ensure amount positive number
            try:
                amt = float(amount)
            except Exception:
                amt = 0.0
            record_transaction(st.session_state.username, str(date), category, amt, note, final_type)
            st.success(f"Added {final_type} transaction: {category} — ₹{amt:.2f}")
            st.rerun()

# --- ANALYTICS ---
elif menu == "📊 Analytics":
    st.subheader("Spending Analytics")
    df = get_user_transactions_df()
    if df.empty:
        st.info("No data available for analysis.")
    else:
        # month selection
        months = sorted(df["Month"].unique(), key=lambda x: datetime.datetime.strptime(x, "%B - %Y"))
        selected_month = st.selectbox("Select Month", months)
        filtered = df[df["Month"] == selected_month]

        # Prepare expense data
        expense_df = filtered[filtered["type"].isin(["Expense", "Savings"])]
        total_income = float(filtered.loc[filtered["type"] == "Income", "amount"].sum())
        total_expense = float(expense_df["amount"].sum())

        # ---------- DONUT PIE: Expense breakdown ----------
        st.markdown("### Expense Distribution (Donut)")
        if not expense_df.empty:
            cat_summary = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)
            labels = cat_summary.index.tolist()
            values = cat_summary.values.tolist()

            fig1, ax1 = plt.subplots(figsize=(5, 5))
            wedges, texts, autotexts = ax1.pie(
                values,
                labels=labels,
                autopct=lambda pct: f"{pct:.1f}%",
                startangle=90,
                wedgeprops={"edgecolor": "white", "linewidth": 0.8},
                pctdistance=0.75,
            )
            # center circle for donut
            centre_circle = plt.Circle((0, 0), 0.55, fc="white")
            fig1.gca().add_artist(centre_circle)
            ax1.axis("equal")
            ax1.set_title("Expenses by Category", fontsize=14)
            plt.setp(autotexts, size=9, weight="bold")
            st.pyplot(fig1)
        else:
            st.info("Not enough expense data to show distribution.")

        # ---------- HORIZONTAL BAR: Top categories ----------
        st.markdown("### Top Expense Categories")
        if not expense_df.empty:
            top_n = min(8, len(expense_df["category"].unique()))
            top_cats = expense_df.groupby("category")["amount"].sum().sort_values(ascending=True).tail(top_n)
            fig2, ax2 = plt.subplots(figsize=(7, 3 + 0.3 * top_n))
            bars = ax2.barh(top_cats.index, top_cats.values)
            ax2.set_xlabel("Amount (₹)")
            ax2.xaxis.set_major_formatter(mtick.StrMethodFormatter("₹{x:,.0f}"))
            ax2.set_title("Top Categories (this month)")
            ax2.grid(axis="x", linestyle="--", alpha=0.25)
            st.pyplot(fig2)
        else:
            st.info("No expense categories to display.")
            
        st.markdown("### Income vs Expense Comparison")

        comparison_labels = ["Income", "Expense"]
        comparison_values = [total_income, total_expense]

        fig_comp, ax_comp = plt.subplots(figsize=(4,3))
        ax_comp.bar(comparison_labels, comparison_values)

        ax_comp.set_ylabel("Amount (₹)")
        ax_comp.set_title("Income vs Expense (This Month)")
        ax_comp.grid(axis="y", linestyle="--", alpha=0.25)

        st.pyplot(fig_comp)

        # ---------- MONTHLY TREND: line + bar combo ----------
        st.markdown("### Monthly Trend (All Transactions)")
        monthly = df.groupby("Month")["amount"].sum().reindex(months)
        fig3, ax3 = plt.subplots(figsize=(6, 2.8))
        ax3.plot(monthly.index, monthly.values, marker="o", linewidth=2)
        ax3.bar(monthly.index, monthly.values, alpha=0.25)
        ax3.set_xticklabels(monthly.index, rotation=45, ha="right")
        ax3.set_ylabel("Amount (₹)")
        ax3.set_title("Total Transactions per Month")
        ax3.grid(axis="y", linestyle="--", alpha=0.25)
        st.pyplot(fig3)

        st.markdown("### Cashflow Trend (Income vs Expense by Month)")

        income_monthly = df[df["type"] == "Income"].groupby("Month")["amount"].sum().reindex(months, fill_value=0)
        expense_monthly = df[df["type"].isin(["Expense","Savings"])].groupby("Month")["amount"].sum().reindex(months, fill_value=0)

        fig_cf, ax_cf = plt.subplots(figsize=(7,3))

        ax_cf.plot(income_monthly.index, income_monthly.values, marker="o", label="Income")
        ax_cf.plot(expense_monthly.index, expense_monthly.values, marker="o", label="Expense")

        ax_cf.set_ylabel("Amount (₹)")
        ax_cf.set_title("Monthly Cashflow Trend")
        ax_cf.legend()

        ax_cf.grid(axis="y", linestyle="--", alpha=0.3)

        plt.xticks(rotation=45)

        st.pyplot(fig_cf)

        # Quick summary metrics
        col1, col2 = st.columns(2)
        col1.metric("Total Income", f"₹{total_income:,.2f}")
        col2.metric("Total Expense", f"₹{total_expense:,.2f}")
# --- BUDGET PLANNER ---
elif menu == "💰 Budget Planner":
    st.subheader("Budget Planner")
    this_month = datetime.datetime.today().strftime("%B - %Y")
    current_budget = retrieve_budget(st.session_state.username, this_month)
    if current_budget:
        st.success(f"Current Budget: ₹{current_budget:.2f}")
    else:
        st.warning("No budget set for this month.")
    members = 1
    if st.session_state.account_type == "Family":
        members = st.number_input("Number of family members (for per-person suggestion)", min_value=1, value=2, step=1)
    new_amount = st.number_input("Set/Update Monthly Budget (₹)", min_value=0.0)
    if st.button("Save Budget"):
        set_budget(st.session_state.username, this_month, new_amount)
        st.success("Budget Updated Successfully!")
        if members > 1:
            st.info(f"Suggested per-person budget: ₹{(new_amount / members):.2f}")

    st.markdown("---")
    st.write("Suggested categories for your profession:")
    prof_cats = get_categories_for_profession(st.session_state.profession)
    st.write(", ".join([c for c, _ in prof_cats]))

# --- CATEGORIES MANAGEMENT ---
elif menu == "🧰 Categories":
    st.subheader("Manage Custom Categories")
    st.write("Add custom categories that will appear in your Add Transaction dropdown (per profession).")
    prof = st.selectbox("For Profession", get_all_professions(), index=get_all_professions().index(st.session_state.profession) if st.session_state.profession in get_all_professions() else 0)
    with st.form("add_cat", clear_on_submit=True):
        new_cat = st.text_input("Category Name")
        new_type = st.selectbox("Type", ["Expense", "Income", "Savings"])
        add_btn = st.form_submit_button("Add Category")
        if add_btn:
            if not new_cat.strip():
                st.error("Category name required.")
            else:
                added = add_custom_category(st.session_state.username, prof, new_cat.strip(), new_type)
                if added:
                    st.success("Custom category added.")
                else:
                    st.error("Could not add (may already exist).")
                st.rerun()

    st.markdown("Your custom categories for selected profession:")
    rows = list_custom_categories(st.session_state.username, prof)
    if rows:
        for rid, cname, ctype in rows:
            cols = st.columns([4, 1])
            cols[0].write(f"{cname} ({ctype})")
            if cols[1].button("Delete", key=f"del_{rid}"):
                removed = remove_custom_category(st.session_state.username, prof, cname)
                if removed:
                    st.success("Deleted.")
                else:
                    st.error("Delete failed.")
                st.rerun()
    else:
        st.write("No custom categories yet.")

# --- AI INSIGHTS ---
elif menu == "🤖 AI Insights":
    st.subheader("🤖 VALORA AI Insights")

    transactions = fetch_transactions(st.session_state.username)
    df = get_user_transactions_df()

    if df.empty:
        st.info("Not enough data for AI insights.")
    else:
        from predictor import predict_future
        result = predict_future(transactions)

        if result is None:
            st.error("⚠️ Prediction failed. Not enough data.")
            st.stop()
        # ---------------- Prediction Metrics ----------------
        st.markdown("### 🔮 Future Predictions")
        # CSS for prediction cards
        st.markdown("""
        <style>
        .pred-card {
            border-radius: 14px;
            padding: 18px;
            text-align: center;
            color: white;
            font-weight: 600;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            transition: transform 0.25s ease;
        }
        .pred-card:hover {
            transform: translateY(-5px);
        }
        .pred-title {
            font-size: 1rem;
            margin-bottom: 5px;
        }
        .pred-value {
            font-size: 1.6rem;
            font-weight: 700;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div class="pred-card" style="background: linear-gradient(135deg,#4facfe,#00f2fe);">
            <div class="pred-title">Weekly Prediction</div>
            <div class="pred-value">₹{result['weekly']}</div>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="pred-card" style="background: linear-gradient(135deg,#43e97b,#38f9d7);">
            <div class="pred-title">Monthly Prediction</div>
            <div class="pred-value">₹{result['monthly']}</div>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="pred-card" style="background: linear-gradient(135deg,#fa709a,#fee140);">
            <div class="pred-title">Yearly Prediction</div>
            <div class="pred-value">₹{result['yearly']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        # ---------------- Budget Warning ----------------
        this_month = datetime.datetime.today().strftime("%B - %Y")
        budget = retrieve_budget(st.session_state.username, this_month)

        if budget:
            if result['monthly'] > budget:
                st.error("⚠️ You are likely to exceed your monthly budget!")
            else:
                st.success("✅ You are within your budget trend.")
        # ---------------- AI Insights ----------------
        st.markdown("### 🧠 Smart Insights")

        if result['yearly'] > 200000:
            st.warning("💡 Your yearly spending is high. Consider reducing unnecessary expenses.")
        elif result['monthly'] < 5000:
            st.success("🎯 Great! Your spending is well controlled.")
        else:
            st.info("ℹ️ Your spending pattern is moderate.")
    
        # ---------------- Category Prediction ----------------
        st.markdown("### 📊 Category-wise Prediction")

        expense_df = df[df["type"].isin(["Expense", "Savings"])]

        if not expense_df.empty:
            category_summary = expense_df.groupby("category")["amount"].sum()
            total_days = (df["Date"].max() - df["Date"].min()).days + 1

            # CSS for cards
            st.markdown("""
            <style>
            .cat-card {
                padding:15px;
                border-radius:12px;
                margin-bottom:10px;
                color:white;
                font-weight:600;
                box-shadow:0 6px 15px rgba(0,0,0,0.15);
            }
            </style>
            """, unsafe_allow_html=True)

            for category, amount in category_summary.items():
                daily_avg = amount / total_days

                weekly = daily_avg * 7
                monthly = daily_avg * 30

                # 🎨 Color logic
                if monthly > 8000:
                    color = "#ff4d4d"   # red
                elif monthly > 3000:
                    color = "#ffa500"   # orange
                else:
                    color = "#28a745"   # green

                st.markdown(f"""
                <div class="cat-card" style="background:{color};">
                    📌 {category}<br>
                    Weekly: ₹{weekly:.0f} &nbsp; | &nbsp;
                    Monthly: ₹{monthly:.0f}
                </div>
                """, unsafe_allow_html=True)

                        # ---------------- AI Advisor ----------------
        st.markdown("### 🤖 VALORA AI Advisor")

        advice = []

        if result['monthly'] > 15000:
            advice.append("Reduce dining and entertainment expenses.")

        if "Food" in expense_df["category"].values:
            advice.append("Try cooking more meals at home to save money.")

        if result['yearly'] > 250000:
            advice.append("Consider setting stricter budgets to control long-term spending.")

        if not advice:
            advice.append("Your finances look healthy. Keep it up!")

        for tip in advice:
            st.write(f"💡 {tip}")

# --- SETTINGS ---
elif menu == "⚙️ Settings":
    st.subheader("Settings & Profile")
    st.write(f"Logged in as: **{st.session_state.username}**")

    col1, col2 = st.columns(2)
    with col1:
        new_prof = st.selectbox("Profession", get_all_professions(), index=get_all_professions().index(st.session_state.profession) if st.session_state.profession in get_all_professions() else 0)
        new_account_type = st.selectbox("Account Type", ["Individual", "Family"], index=0 if st.session_state.account_type == "Individual" else 1)
        if st.button("Update Profile"):
            if update_user_profile(st.session_state.username, new_prof, new_account_type):
                st.session_state.profession = new_prof
                st.session_state.account_type = new_account_type
                st.success("Profile updated.")
            else:
                st.error("Could not update profile.")
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# Footer (single consistent footer)
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Developed by Team VALORA<b> </b></p>", unsafe_allow_html=True)
