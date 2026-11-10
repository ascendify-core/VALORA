import pandas as pd

def predict_future(transactions):
    df = pd.DataFrame(transactions)

    if len(df) < 3:
        return None

    # Convert date
    df['date'] = pd.to_datetime(df['date'])

    # Sort by date
    df = df.sort_values(by='date')

    # Calculate daily spending
    total_days = (df['date'].max() - df['date'].min()).days + 1
    total_spent = df['amount'].sum()

    daily_avg = total_spent / total_days

    # Predictions
    weekly = daily_avg * 7
    monthly = daily_avg * 30
    yearly = daily_avg * 365

    return {
        "daily_avg": round(daily_avg, 2),
        "weekly": round(weekly, 2),
        "monthly": round(monthly, 2),
        "yearly": round(yearly, 2)
    }