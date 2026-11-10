import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from budget import fetch_transactions

def analytics_page(username: str, profession: str = "Individual"):
    st.title("📊 Financial Analytics")
    tx = fetch_transactions(username)
    if not tx:
        st.info("No data yet to show analytics.")
        return

    df = pd.DataFrame(tx)
    if 'date' in df.columns:
        df['Date'] = pd.to_datetime(df['date'])
    elif 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    else:
        st.error("Transaction data missing 'date' field.")
        return

    df['Month'] = df['Date'].dt.strftime('%B - %Y')
    selected_month = st.selectbox("Select Month", sorted(df['Month'].unique()))
    filtered_df = df[df['Month'] == selected_month]

    expense_df = filtered_df[filtered_df['type'].isin(['Expense', 'Savings'])]
    if not expense_df.empty:
        category_summary = expense_df.groupby('category')['amount'].sum().sort_values(ascending=False)
        st.subheader("Category-wise Spending")
        fig, ax = plt.subplots()
        ax.pie(category_summary, labels=category_summary.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.info("No Expense/Savings data to show category chart.")

    st.subheader("Monthly Trend (All Transactions)")
    monthly_summary = df.groupby('Month')['amount'].sum()
    fig2, ax2 = plt.subplots()
    monthly_summary.plot(kind='bar', ax=ax2)
    ax2.set_ylabel("Amount")
    ax2.set_xlabel("Month")
    st.pyplot(fig2)

    st.markdown("---")
    st.subheader("Quick Insights")
    if not expense_df.empty:
        top_categories = expense_df.groupby('category')['amount'].sum().sort_values(ascending=False).head(5)
        st.write("Top expense categories this month:")
        st.table(top_categories.reset_index().rename(columns={'index': 'Category', 'amount': 'Amount'}))
    st.write("Note: Analytics are generic. Profession-specific analytics can be enabled later.")
