"""
Data generation and file parsing module for SentientSpend
Handles demo data creation and CSV/Excel/JSON upload
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime
import streamlit as st

def generate_demo_data(months=12, base_salary=50000):
    """
    Generate realistic 12-month financial transaction data
    
    Parameters:
    - months: number of months to generate
    - base_salary: initial monthly salary
    
    Returns: pandas DataFrame with transaction data
    """
    np.random.seed(42)
    random.seed(42)
    
    months_range = pd.date_range(start="2024-01-01", periods=months, freq='MS')
    categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment"]
    rows = []
    current_salary = base_salary
    
    for i, month in enumerate(months_range):
        # Salary increment every 3 months
        if i % 3 == 0 and i != 0:
            current_salary += 3000
        
        rows.append({
            "Date": month,
            "Type": "Income",
            "Category": "Salary",
            "Amount": current_salary,
            "Description": "Monthly Salary"
        })
        
        # Generate 6-10 expenses per month
        num_expenses = np.random.randint(6, 11)
        
        for _ in range(num_expenses):
            expense_date = month + pd.Timedelta(days=np.random.randint(1, 27))
            is_weekend = expense_date.weekday() >= 5
            
            if is_weekend:
                category = random.choice(["Shopping", "Entertainment", "Food"])
                amount = np.random.randint(2000, 9000)
            else:
                category = random.choice(categories)
                if category in ["Shopping", "Bills"]:
                    amount = np.random.randint(1500, 6000)
                else:
                    amount = np.random.randint(500, 4000)
            
            rows.append({
                "Date": expense_date,
                "Type": "Expense",
                "Category": category,
                "Amount": amount,
                "Description": f"{category} Expense"
            })
    
    df = pd.DataFrame(rows)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M")
    
    return df


def parse_upload(uploaded_file):
    """
    Parse uploaded CSV/Excel/JSON file and convert to standard format
    
    Parameters:
    - uploaded_file: streamlit uploaded file object
    
    Returns: pandas DataFrame
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.json'):
            df = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file format. Please use CSV, Excel, or JSON.")
            return None
        
        # Validate required columns
        required_cols = ["Date", "Type", "Category", "Amount"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"Missing required columns: {required_cols}")
            return None
        
        df["Date"] = pd.to_datetime(df["Date"])
        df["Month"] = df["Date"].dt.to_period("M")
        
        return df
    
    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")
        return None


def compute_monthly_summary(df):
    """
    Compute monthly income, expense, and savings summary
    
    Parameters:
    - df: transaction DataFrame
    
    Returns: pandas DataFrame with monthly summary
    """
    monthly_income = df[df["Type"] == "Income"].groupby("Month")["Amount"].sum()
    monthly_expense = df[df["Type"] == "Expense"].groupby("Month")["Amount"].sum()
    
    summary = pd.DataFrame({
        "Income": monthly_income,
        "Expense": monthly_expense
    })
    
    summary["Savings"] = summary["Income"] - summary["Expense"]
    
    return summary


def compute_category_summary(df):
    """
    Compute total expense by category
    
    Parameters:
    - df: transaction DataFrame
    
    Returns: pandas Series with category totals
    """
    return df[df["Type"] == "Expense"].groupby("Category")["Amount"].sum().sort_values(ascending=False)