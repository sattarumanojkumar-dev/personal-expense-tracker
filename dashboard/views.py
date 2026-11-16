import json
from datetime import date
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from expenses.sql_queries import (
    get_dashboard_summary,
    get_recent_expenses_sql,
    get_monthly_spending_trend,
    get_category_spending_sql,
)

@login_required
def dashboard_view(request):
    """
    Main dashboard view.
    Dynamically executes parameterized SQL queries to calculate metrics
    and prepare Chart.js datasets for the logged-in user.
    """
    user_id = request.user.id
    current_date = date.today()

    # 1. Summary Cards (Calculated directly via SQL)
    summary = get_dashboard_summary(user_id)

    # 2. Recent Transactions (Latest 5 expenses for current user)
    recent_transactions = get_recent_expenses_sql(user_id, limit=5)

    # 3. Monthly Spending Trend (Last 6 months comparison)
    trend_data = get_monthly_spending_trend(user_id, num_months=6)

    # 4. Category Spending Analysis (Aggregated via SQL)
    category_data = get_category_spending_sql(user_id)

    context = {
        'summary': summary,
        'recent_transactions': recent_transactions,
        'trend_labels_json': json.dumps(trend_data['labels']),
        'trend_values_json': json.dumps(trend_data['data']),
        'category_labels_json': json.dumps(category_data['categories']),
        'category_values_json': json.dumps(category_data['totals']),
        'current_date': current_date,
        'active_page': 'dashboard',
    }
    return render(request, 'dashboard/index.html', context)
