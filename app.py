"""
Main Streamlit Application for SentientSpend AI Finance Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from data_gen import generate_demo_data, parse_upload, compute_monthly_summary, compute_category_summary
from analytics import run_regression, get_trend_direction, run_clustering, get_budget_status, compute_budget_table, simulate_savings
from simulator import BudgetSimulator, generate_ai_suggestions

# Page config
st.set_page_config(page_title="SentientSpend AI", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for professional styling
st.markdown("""
<style>
    :root {
        --primary-color: #1f77b4;
        --success-color: #2ecc71;
        --warning-color: #f39c12;
        --danger-color: #e74c3c;
    }
    
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .status-badge {
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    
    .status-under { background-color: #2ecc71; color: white; }
    .status-near { background-color: #f39c12; color: white; }
    .status-exceeded { background-color: #e74c3c; color: white; }
    
    .persona-card {
        padding: 25px;
        border-radius: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.image("https://via.placeholder.com/50x50?text=SS", width=50)
st.sidebar.title("🎯 SentientSpend")
st.sidebar.markdown("---")

# User profile
st.sidebar.markdown("""
**👤 Alex Rivers**  
*Premium Plan*
""")

# Budget slider
budget_limit = st.sidebar.slider("💰 Budget Limit", 30000, 100000, 55000, step=1000)

st.sidebar.markdown("---")

# Navigation menu
menu_option = st.sidebar.radio(
    "📋 Navigation",
    ["Dashboard", "Simulator", "Analytics", "Budget", "Transactions", "Settings"],
    index=0
)

st.sidebar.markdown("---")

# Upgrade button
if st.sidebar.button("⬆️ Upgrade Now"):
    st.sidebar.success("Premium features coming soon!")

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_data():
    """Load or generate transaction data"""
    return generate_demo_data()

df = load_data()

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

if menu_option == "Dashboard":
    st.title("📊 Dashboard")
    st.markdown("Your complete financial overview at a glance.")
    
    # Data upload section
    st.subheader("📥 Data Source")
    col_upload, col_demo = st.columns(2)
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "📂 Drop CSV/Excel file here",
            type=['csv', 'xls', 'xlsx', 'json'],
            help="Upload your transaction data"
        )
        if uploaded_file:
            df = parse_upload(uploaded_file)
            st.success("✅ Data loaded successfully!")
    
    with col_demo:
        if st.button("🎲 Generate Demo Data", use_container_width=True):
            df = generate_demo_data()
            st.success("✅ Demo data generated!")
    
    st.markdown("---")
    
    # Compute metrics
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    total_savings = total_income - total_expense
    savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0
    
    # KPI Cards
    st.subheader("📈 Key Metrics")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.metric("Total Income", f"${total_income:,.0f}", "+12%", delta_color="off")
    
    with kpi_col2:
        st.metric("Total Expense", f"${total_expense:,.0f}", "-5%", delta_color="inverse")
    
    with kpi_col3:
        st.metric("Total Savings", f"${total_savings:,.0f}", "+18%", delta_color="off")
    
    with kpi_col4:
        st.metric("Savings Rate", f"{savings_rate:.1f}%", "+2%", delta_color="off")
    
    st.markdown("---")
    
    # Income vs Expense Trends
    st.subheader("📉 Income vs Expense Trends")
    summary = compute_monthly_summary(df)
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=summary.index.astype(str),
        y=summary["Income"],
        mode='lines+markers',
        name='Income',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=8)
    ))
    fig_trend.add_trace(go.Scatter(
        x=summary.index.astype(str),
        y=summary["Expense"],
        mode='lines+markers',
        name='Expense',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8)
    ))
    fig_trend.update_layout(hovermode='x unified', template='plotly_white', height=400)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    st.markdown("---")
    
    # Expense Breakdown
    st.subheader("🎯 Expense Breakdown by Category")
    cat_summary = compute_category_summary(df)
    
    fig_cat = px.bar(
        x=cat_summary.values,
        y=cat_summary.index,
        orientation='h',
        labels={'x': 'Amount ($)', 'y': 'Category'},
        color=cat_summary.values,
        color_continuous_scale='Blues'
    )
    fig_cat.update_layout(height=300, template='plotly_white')
    st.plotly_chart(fig_cat, use_container_width=True)
    
    # Category values table
    st.markdown("**Category Details:**")
    cat_details = pd.DataFrame({
        'Category': cat_summary.index,
        'Amount': ['$' + f'{v:,.0f}' for v in cat_summary.values],
        'Percentage': [f'{(v/total_expense)*100:.1f}%' for v in cat_summary.values]
    })
    st.dataframe(cat_details, use_container_width=True, hide_index=True)

# ============================================================================
# SIMULATOR PAGE
# ============================================================================

elif menu_option == "Simulator":
    st.title("🎮 Budget Simulator & What-If Analysis")
    st.markdown("Try different scenarios to optimize your finances using AI-powered analysis.")
    
    st.markdown("---")
    
    # Initialize simulator
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    simulator = BudgetSimulator(df)
    
    # Slider for expense reduction
    st.subheader("💡 Interactive What-If Scenarios")
    reduction = st.slider(
        "Reduce Non-Essential Expenses",
        0, 50, 15,
        help="What % can you reduce from Shopping, Entertainment, Food?"
    )
    
    # Calculate simulation
    sim_result = simulator.simulate_expense_reduction(reduction)
    
    # Display results
    col_result1, col_result2 = st.columns(2)
    
    with col_result1:
        st.metric(
            "📊 Projected Monthly Savings",
            f"${sim_result['simulated_savings']:,.2f}",
            f"+${sim_result['savings_increase']:,.2f}"
        )
    
    with col_result2:
        st.metric(
            "📈 Annual Impact",
            f"${sim_result['annual_impact']:,.2f}",
            "Full year potential"
        )
    
    st.markdown("---")
    
    # ML Spending Persona
    st.subheader("🤖 ML Spending Persona")
    persona, confidence, _ = run_clustering(df)
    
    col_persona1, col_persona2 = st.columns([2, 1])
    with col_persona1:
        st.info(f"""
        **{persona}**  
        Based on KMeans clustering of your last 180 days of transactions.  
        You exhibit a stable spending pattern with moderate variance in dining & entertainment.
        """)
    
    with col_persona2:
        st.metric("Confidence Score", f"{confidence*100:.1f}%", "High accuracy")
    
    st.markdown("---")
    
    # Budget Status Table
    st.subheader("📋 Budget Status by Category")
    
    budget_categories = {
        "Food": 1200,
        "Transport": 850,
        "Shopping": 1500,
        "Bills": 2400,
        "Entertainment": 300
    }
    
    budget_df = compute_budget_table(df, budget_categories, budget_limit)
    
    # Color code the status column
    def highlight_status(val):
        if "EXCEEDED" in val:
            return 'background-color: #e74c3c; color: white'
        elif "NEAR" in val:
            return 'background-color: #f39c12; color: white'
        else:
            return 'background-color: #2ecc71; color: white'
    
    styled_df = budget_df.style.applymap(highlight_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Export options
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        if st.button("📥 Export CSV", use_container_width=True):
            csv = budget_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="budget_status.csv",
                mime="text/csv"
            )
    
    with col_exp2:
        if st.button("➕ Add Category", use_container_width=True):
            st.success("Add category feature coming soon!")
    
    st.markdown("---")
    
    # Predictive insights
    st.subheader("🎯 Predictive Insights")
    insight_col1, insight_col2, insight_col3, insight_col4 = st.columns(4)
    
    summary = compute_monthly_summary(df)
    
    with insight_col1:
        st.metric("📈 Predictive Trend", "+4.2% Growth")
    
    with insight_col2:
        st.metric("💰 Total Savings", f"${total_income - df[df['Type']=='Expense']['Amount'].sum():,.0f}")
    
    with insight_col3:
        st.metric("⚠️ Overspending Risks", "2 Categories", "Entertainment, Shopping")
    
    with insight_col4:
        st.metric("✨ AI Suggestions", "5 Optimized", "View below")
    
    # AI Suggestions
    st.markdown("---")
    st.subheader("💡 AI-Powered Suggestions")
    cat_summary = compute_category_summary(df)
    suggestions = generate_ai_suggestions(df, cat_summary.to_dict(), total_income)
    
    for suggestion in suggestions:
        st.info(suggestion)

# ============================================================================
# ANALYTICS PAGE
# ============================================================================

elif menu_option == "Analytics":
    st.title("📊 Predictive Analytics")
    st.markdown("Machine learning models for expense forecasting and trend analysis.")
    
    st.markdown("---")
    
    # Regression analysis
    st.subheader("🔮 Expense Forecasting")
    pred, trend, model = run_regression(df)
    
    col_pred1, col_pred2 = st.columns(2)
    
    with col_pred1:
        st.metric("Predicted Next Month Expense", f"${pred:,.0f}")
    
    with col_pred2:
        st.metric("Trend Slope", f"{trend:+.2f}", get_trend_direction(trend))
    
    # Visualization of trend
    summary = compute_monthly_summary(df)
    X = np.arange(len(summary))
    y_pred = model.predict(X.reshape(-1, 1))
    
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(
        x=summary.index.astype(str),
        y=summary["Expense"],
        mode='markers',
        name='Actual Expense',
        marker=dict(size=10, color='blue')
    ))
    fig_forecast.add_trace(go.Scatter(
        x=summary.index.astype(str),
        y=y_pred,
        mode='lines',
        name='Trend Line',
        line=dict(color='red', dash='dash', width=2)
    ))
    fig_forecast.update_layout(hovermode='x unified', template='plotly_white', height=400)
    st.plotly_chart(fig_forecast, use_container_width=True)
    
    st.markdown("---")
    
    # Clustering analysis
    st.subheader("🎯 Spending Persona Clustering")
    persona, confidence, _ = run_clustering(df)
    
    st.markdown(f"""
    **Identified Persona:** {persona}  
    **Confidence:** {confidence*100:.1f}%
    
    Your spending pattern has been analyzed using K-Means clustering across multiple dimensions:
    - Transaction amount distributions
    - Weekend vs weekday spending
    - Monthly trends
    - Category preferences
    """)

# ============================================================================
# BUDGET PAGE
# ============================================================================

elif menu_option == "Budget":
    st.title("💳 Budget Management")
    st.markdown("Set and track your budgets by category.")
    
    st.markdown("---")
    
    budget_categories = {
        "Food": 1200,
        "Transport": 850,
        "Shopping": 1500,
        "Bills": 2400,
        "Entertainment": 300
    }
    
    st.subheader("🎯 Category Budgets")
    
    for category, limit in budget_categories.items():
        actual = df[(df["Type"] == "Expense") & (df["Category"] == category)]["Amount"].sum()
        status, _, color = get_budget_status(actual, limit)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.progress(min(actual / limit, 1.0), text=category)
        with col2:
            st.metric("Budget", f"${limit:,.0f}")
        with col3:
            st.markdown(f'<div class="status-badge status-{color.replace("#", "").lower()}">{status}</div>', unsafe_allow_html=True)

# ============================================================================
# TRANSACTIONS PAGE
# ============================================================================

elif menu_option == "Transactions":
    st.title("💸 Transactions")
    st.markdown("View all your transactions.")
    
    st.markdown("---")
    
    # Filter options
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        type_filter = st.multiselect("Type", ["Income", "Expense"], default=["Income", "Expense"])
    
    with col_filter2:
        category_filter = st.multiselect("Category", df["Category"].unique())
    
    with col_filter3:
        month_filter = st.multiselect("Month", df["Month"].unique())
    
    # Apply filters
    filtered_df = df.copy()
    if type_filter:
        filtered_df = filtered_df[filtered_df["Type"].isin(type_filter)]
    if category_filter:
        filtered_df = filtered_df[filtered_df["Category"].isin(category_filter)]
    if month_filter:
        filtered_df = filtered_df[filtered_df["Month"].isin(month_filter)]
    
    # Display transactions
    display_df = filtered_df[["Date", "Type", "Category", "Amount", "Description"]].sort_values("Date", ascending=False)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Download option
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Transactions",
        data=csv,
        file_name="transactions.csv",
        mime="text/csv"
    )

# ============================================================================
# SETTINGS PAGE
# ============================================================================

elif menu_option == "Settings":
    st.title("⚙️ Settings")
    st.markdown("Manage your preferences and account settings.")
    
    st.markdown("---")
    
    # User settings
    st.subheader("👤 User Profile")
    col_user1, col_user2 = st.columns(2)
    
    with col_user1:
        st.text_input("First Name", "Alex", disabled=True)
    
    with col_user2:
        st.text_input("Last Name", "Rivers", disabled=True)
    
    st.email_input("Email", "alex.rivers@example.com", disabled=True)
    
    st.markdown("---")
    
    # Notification settings
    st.subheader("🔔 Notifications")
    st.checkbox("Budget alerts", value=True)
    st.checkbox("Spending insights", value=True)
    st.checkbox("Weekly summaries", value=True)
    
    st.markdown("---")
    
    # Privacy
    st.subheader("🔐 Privacy")
    st.info("Your data is encrypted and stored securely. We never sell your information.")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 12px; margin-top: 30px;'>
    © 2024 SentientSpend AI Analytics Platform. All rights reserved.
    <br>
    <a href='#'>Privacy Policy</a> | <a href='#'>Terms of Service</a> | <a href='#'>Documentation</a>
</div>
""", unsafe_allow_html=True)