"""
What-If Scenario Simulator for SentientSpend
Allows users to test different budget scenarios and visualize impact
"""

import pandas as pd
import numpy as np


class BudgetSimulator:
    def __init__(self, df):
        """
        Initialize simulator with transaction data
        
        Parameters:
        - df: transaction DataFrame
        """
        self.df = df
        self.base_expense = df[df["Type"] == "Expense"]["Amount"].sum()
        self.base_income = df[df["Type"] == "Income"]["Amount"].sum()
        self.base_savings = self.base_income - self.base_expense
    
    def simulate_expense_reduction(self, reduction_percent):
        """
        Simulate reducing non-essential expenses
        
        Parameters:
        - reduction_percent: percentage to reduce (0-100)
        
        Returns: dict with results
        """
        non_essential = ["Shopping", "Entertainment", "Food"]
        expense_df = self.df[self.df["Type"] == "Expense"]
        
        non_essential_total = expense_df[expense_df["Category"].isin(non_essential)]["Amount"].sum()
        reduction = (non_essential_total * reduction_percent) / 100
        
        new_total_expense = self.base_expense - reduction
        new_savings = self.base_income - new_total_expense
        savings_increase = new_savings - self.base_savings
        
        return {
            "current_expense": self.base_expense,
            "simulated_expense": new_total_expense,
            "reduction_amount": reduction,
            "current_savings": self.base_savings,
            "simulated_savings": new_savings,
            "savings_increase": savings_increase,
            "annual_impact": savings_increase * 12
        }
    
    def simulate_income_increase(self, increase_percent):
        """
        Simulate income increase impact
        
        Parameters:
        - increase_percent: percentage increase
        
        Returns: dict with results
        """
        increase = (self.base_income * increase_percent) / 100
        new_income = self.base_income + increase
        new_savings = new_income - self.base_expense
        
        return {
            "current_income": self.base_income,
            "simulated_income": new_income,
            "income_increase": increase,
            "current_savings": self.base_savings,
            "simulated_savings": new_savings,
            "savings_increase": new_savings - self.base_savings
        }
    
    def simulate_category_budget(self, category, new_budget):
        """
        Simulate adjusting budget for specific category
        
        Parameters:
        - category: expense category
        - new_budget: new budget limit
        
        Returns: dict with results
        """
        expense_df = self.df[self.df["Type"] == "Expense"]
        category_current = expense_df[expense_df["Category"] == category]["Amount"].sum()
        
        adjustment = category_current - new_budget
        new_total_expense = self.base_expense - adjustment
        new_savings = self.base_income - new_total_expense
        
        return {
            "category": category,
            "current_spending": category_current,
            "new_budget": new_budget,
            "adjustment": adjustment,
            "new_total_savings": new_savings,
            "savings_impact": new_savings - self.base_savings
        }


def generate_ai_suggestions(df, expense_by_category, total_income):
    """
    Generate AI-powered spending optimization suggestions
    
    Parameters:
    - df: transaction DataFrame
    - expense_by_category: dict of category expenses
    - total_income: total monthly income
    
    Returns: list of suggestion strings
    """
    suggestions = []
    
    # Analyze spending patterns
    for category, amount in expense_by_category.items():
        percent_of_income = (amount / total_income) * 100
        
        if category == "Food" and percent_of_income > 15:
            suggestions.append(f"💡 {category} is {percent_of_income:.1f}% of income. Consider meal planning to reduce to ~10%.")
        elif category == "Transport" and percent_of_income > 12:
            suggestions.append(f"💡 {category} is {percent_of_income:.1f}% of income. Explore carpooling or public transit savings.")
        elif category == "Entertainment" and percent_of_income > 8:
            suggestions.append(f"💡 {category} is {percent_of_income:.1f}% of income. Try reducing subscription services.")
        elif category == "Shopping" and percent_of_income > 10:
            suggestions.append(f"💡 {category} is {percent_of_income:.1f}% of income. Set a discretionary spending limit.")
    
    # Overall suggestions
    total_expense = sum(expense_by_category.values())
    savings_rate = ((total_income - total_expense) / total_income) * 100
    
    if savings_rate < 10:
        suggestions.append("🎯 Your savings rate is low. Target at least 15-20% for financial health.")
    elif savings_rate > 30:
        suggestions.append("🎉 Excellent savings rate! Consider investing the extra funds.")
    
    return suggestions if suggestions else ["✨ Your spending looks optimized!"]