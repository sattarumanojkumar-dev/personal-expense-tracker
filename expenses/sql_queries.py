"""
Raw SQL Analytics and Reporting Queries for Personal Expense Tracker.
Uses parameterized SQL queries via django.db.connection to guarantee:
1. SQL-level data aggregation and reporting.
2. Complete user-level data isolation.
3. Strict protection against SQL injection.
"""
from decimal import Decimal
import calendar
from datetime import date, datetime
from django.db import connection

def _get_month_bounds(year: int, month: int):
    """Return (start_date, end_date) for a given year and month."""
    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    return start_date, end_date

def _prev_month_year(year: int, month: int):
    """Return (prev_year, prev_month)."""
    if month == 1:
        return year - 1, 12
    return year, month - 1


def get_dashboard_summary(user_id: int):
    """
    Execute SQL queries to calculate:
    1. Total Expenses
    2. This Month's Expenses
    3. Today's Expenses
    4. Total Number of Transactions
    Strictly isolated to user_id.
    """
    today = date.today()
    start_of_month, end_of_month = _get_month_bounds(today.year, today.month)

    with connection.cursor() as cursor:
        # 1. Total Expenses and Total Transactions
        cursor.execute("""
            SELECT 
                COALESCE(SUM(amount), 0) AS total_amount,
                COUNT(id) AS total_count
            FROM expenses
            WHERE user_id = %s
        """, [user_id])
        row_total = cursor.fetchone()
        total_amount = Decimal(str(row_total[0])) if row_total else Decimal('0.00')
        total_count = int(row_total[1]) if row_total else 0

        # 2. This Month's Expenses
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE user_id = %s AND expense_date >= %s AND expense_date <= %s
        """, [user_id, start_of_month, end_of_month])
        row_month = cursor.fetchone()
        month_amount = Decimal(str(row_month[0])) if row_month else Decimal('0.00')

        # 3. Today's Expenses
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE user_id = %s AND expense_date = %s
        """, [user_id, today])
        row_today = cursor.fetchone()
        today_amount = Decimal(str(row_today[0])) if row_today else Decimal('0.00')

    return {
        'total_amount': total_amount,
        'month_amount': month_amount,
        'today_amount': today_amount,
        'total_count': total_count,
    }


def get_recent_expenses_sql(user_id: int, limit: int = 5):
    """
    Fetch the latest transactions for user_id using SQL.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title, amount, category, payment_method, expense_date, description
            FROM expenses
            WHERE user_id = %s
            ORDER BY expense_date DESC, created_at DESC
            LIMIT %s
        """, [user_id, limit])
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
    return [dict(zip(columns, row)) for row in rows]


def get_monthly_spending_trend(user_id: int, num_months: int = 6):
    """
    Calculate spending across the last `num_months` months (ending at current month).
    Returns list of labels and list of amounts for Chart.js.
    """
    today = date.today()
    curr_y = today.year
    curr_m = today.month

    # Generate months list from oldest to newest
    months_list = []
    y, m = curr_y, curr_m
    for _ in range(num_months):
        months_list.append((y, m))
        y, m = _prev_month_year(y, m)
    months_list.reverse()

    labels = []
    data = []

    with connection.cursor() as cursor:
        for yr, mo in months_list:
            s_date, e_date = _get_month_bounds(yr, mo)
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM expenses
                WHERE user_id = %s AND expense_date >= %s AND expense_date <= %s
            """, [user_id, s_date, e_date])
            row = cursor.fetchone()
            val = float(row[0]) if row else 0.0
            month_name = calendar.month_abbr[mo]
            labels.append(f"{month_name} {yr}")
            data.append(val)

    return {
        'labels': labels,
        'data': data
    }


def get_category_spending_sql(user_id: int, year: int = None, month: int = None):
    """
    Aggregate expenses by category for a user, optionally filtered by month and year.
    Returns categories, totals, and counts.
    """
    query = """
        SELECT category, COALESCE(SUM(amount), 0) as total, COUNT(id) as count
        FROM expenses
        WHERE user_id = %s
    """
    params = [user_id]

    if year and month:
        s_date, e_date = _get_month_bounds(year, month)
        query += " AND expense_date >= %s AND expense_date <= %s"
        params.extend([s_date, e_date])

    query += " GROUP BY category ORDER BY total DESC"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    categories = []
    totals = []
    counts = []
    items = []

    for row in rows:
        cat = row[0]
        tot = float(row[1])
        cnt = int(row[2])
        categories.append(cat)
        totals.append(tot)
        counts.append(cnt)
        items.append({'category': cat, 'total': Decimal(str(row[1])), 'count': cnt})

    return {
        'categories': categories,
        'totals': totals,
        'counts': counts,
        'items': items
    }


def get_monthly_report_data(user_id: int, year: int, month: int):
    """
    Generate comprehensive monthly report data:
    1. Selected month total and transaction count
    2. Previous month total and transaction count
    3. Comparison metrics (diff and percentage change)
    4. Category breakdown with percentages
    5. Daily spending breakdown for trend visualization
    """
    # 1. Selected month bounds
    sel_start, sel_end = _get_month_bounds(year, month)
    # 2. Previous month bounds
    prev_y, prev_m = _prev_month_year(year, month)
    prev_start, prev_end = _get_month_bounds(prev_y, prev_m)

    with connection.cursor() as cursor:
        # Selected month total & count
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0), COUNT(id)
            FROM expenses
            WHERE user_id = %s AND expense_date >= %s AND expense_date <= %s
        """, [user_id, sel_start, sel_end])
        sel_row = cursor.fetchone()
        sel_total = Decimal(str(sel_row[0])) if sel_row else Decimal('0.00')
        sel_count = int(sel_row[1]) if sel_row else 0

        # Previous month total & count
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0), COUNT(id)
            FROM expenses
            WHERE user_id = %s AND expense_date >= %s AND expense_date <= %s
        """, [user_id, prev_start, prev_end])
        prev_row = cursor.fetchone()
        prev_total = Decimal(str(prev_row[0])) if prev_row else Decimal('0.00')
        prev_count = int(prev_row[1]) if prev_row else 0

        # Category breakdown for selected month
        cursor.execute("""
            SELECT category, COALESCE(SUM(amount), 0) as cat_total, COUNT(id) as cat_count
            FROM expenses
            WHERE user_id = %s AND expense_date >= %s AND expense_date <= %s
            GROUP BY category
            ORDER BY cat_total DESC
        """, [user_id, sel_start, sel_end])
        cat_rows = cursor.fetchall()

        # Daily spending breakdown
        cursor.execute("""
            SELECT expense_date, COALESCE(SUM(amount), 0) as day_total, COUNT(id) as day_count
            FROM expenses
            WHERE user_id = %s AND expense_date >= %s AND expense_date <= %s
            GROUP BY expense_date
            ORDER BY expense_date ASC
        """, [user_id, sel_start, sel_end])
        daily_rows = cursor.fetchall()

    # Calculate difference and percentage
    diff = sel_total - prev_total
    if prev_total > 0:
        pct_change = round(((sel_total - prev_total) / prev_total) * 100, 1)
    else:
        pct_change = 100.0 if sel_total > 0 else 0.0

    category_breakdown = []
    cat_names = []
    cat_totals = []
    for cat, tot, cnt in cat_rows:
        tot_dec = Decimal(str(tot))
        pct = round((tot_dec / sel_total * 100), 1) if sel_total > 0 else 0.0
        category_breakdown.append({
            'category': cat,
            'total': tot_dec,
            'count': cnt,
            'percentage': pct
        })
        cat_names.append(cat)
        cat_totals.append(float(tot))

    daily_labels = [row[0].strftime("%d %b") for row in daily_rows]
    daily_amounts = [float(row[1]) for row in daily_rows]

    return {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'prev_year': prev_y,
        'prev_month': prev_m,
        'prev_month_name': calendar.month_name[prev_m],
        'current_month_total': sel_total,
        'current_month_count': sel_count,
        'prev_month_total': prev_total,
        'prev_month_count': prev_count,
        'diff': diff,
        'pct_change': pct_change,
        'is_increase': diff > 0,
        'category_breakdown': category_breakdown,
        'cat_names': cat_names,
        'cat_totals': cat_totals,
        'daily_labels': daily_labels,
        'daily_amounts': daily_amounts,
    }
