from datetime import date, datetime
import calendar
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404, JsonResponse

from .models import Expense, CATEGORY_CHOICES, PAYMENT_METHOD_CHOICES
from .forms import ExpenseForm
from .sql_queries import (
    get_monthly_report_data,
    get_category_spending_sql,
    get_monthly_spending_trend
)

@login_required
def expense_list_view(request):
    """
    View all expenses belonging strictly to the logged-in user.
    Supports:
    - Search by Title, Category, and Date
    - Filter by Category
    - Filter by Month and Year
    - Filter by Date Range (start_date to end_date)
    - Pagination
    """
    user = request.user
    # Strict backend data isolation: Only filter for current user
    queryset = Expense.objects.filter(user=user)

    # 1. Search query (Title or Description)
    search_query = request.GET.get('q', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # 2. Category filter
    selected_category = request.GET.get('category', '').strip()
    if selected_category:
        queryset = queryset.filter(category=selected_category)

    # 3. Specific Date filter
    date_filter = request.GET.get('date', '').strip()
    if date_filter:
        try:
            parsed_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            queryset = queryset.filter(expense_date=parsed_date)
        except ValueError:
            pass

    # 4. Month & Year filter
    month_filter = request.GET.get('month', '').strip()
    year_filter = request.GET.get('year', '').strip()
    if month_filter and year_filter:
        try:
            m = int(month_filter)
            y = int(year_filter)
            queryset = queryset.filter(expense_date__year=y, expense_date__month=m)
        except ValueError:
            pass
    elif year_filter:
        try:
            y = int(year_filter)
            queryset = queryset.filter(expense_date__year=y)
        except ValueError:
            pass

    # Total amount for the current filtered queryset
    total_filtered_amount = sum(item.amount for item in queryset)

    # Pagination: 10 expenses per page
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    # Year choices for filtering (e.g. 5 years back to current year)
    current_year = date.today().year
    years_range = list(range(current_year - 4, current_year + 2))
    months_range = [(i, calendar.month_name[i]) for i in range(1, 13)]

    context = {
        'page_obj': page_obj,
        'categories': CATEGORY_CHOICES,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_date': date_filter,
        'selected_month': int(month_filter) if month_filter.isdigit() else '',
        'selected_year': int(year_filter) if year_filter.isdigit() else '',
        'years_range': years_range,
        'months_range': months_range,
        'total_filtered_amount': total_filtered_amount,
        'total_records_count': queryset.count(),
        'active_page': 'expenses',
    }
    return render(request, 'expenses/expense_list.html', context)


@login_required
def expense_create_view(request):
    """
    Add a new expense.
    Ensures:
    - User ownership is strictly set to request.user.
    - Amount > 0.
    """
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # Secure server-side association
            expense.save()
            messages.success(request, f"Expense '{expense.title}' of ₹{expense.amount} was saved successfully!")
            return redirect('expense_list')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ExpenseForm()

    context = {
        'form': form,
        'is_edit': False,
        'active_page': 'add_expense'
    }
    return render(request, 'expenses/expense_form.html', context)


@login_required
def expense_update_view(request, pk):
    """
    Update an existing expense.
    Security: Strictly verifies ownership with request.user.
    Raises 404 if expense does not belong to the user.
    """
    # Strict ownership verification
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            updated_expense = form.save()
            messages.success(request, f"Expense '{updated_expense.title}' updated successfully!")
            return redirect('expense_list')
        else:
            messages.error(request, "Please check the values and correct the errors.")
    else:
        form = ExpenseForm(instance=expense)

    context = {
        'form': form,
        'expense': expense,
        'is_edit': True,
        'active_page': 'expenses'
    }
    return render(request, 'expenses/expense_form.html', context)


@login_required
def expense_delete_view(request, pk):
    """
    Delete an existing expense.
    Security: Strictly verifies ownership with request.user.
    Raises 404 if expense does not belong to the user.
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        title = expense.title
        amount = expense.amount
        expense.delete()
        messages.success(request, f"Expense '{title}' (₹{amount}) has been deleted.")
        return redirect('expense_list')

    context = {
        'expense': expense,
        'active_page': 'expenses'
    }
    return render(request, 'expenses/expense_confirm_delete.html', context)


@login_required
def monthly_reports_view(request):
    """
    Generate Monthly Reports using SQL aggregation:
    - Month and Year selector
    - Current vs Previous month comparison
    - Category-wise breakdown
    - Daily spending trends
    - Data for Chart.js
    """
    today = date.today()
    try:
        selected_year = int(request.GET.get('year', today.year))
    except (ValueError, TypeError):
        selected_year = today.year

    try:
        selected_month = int(request.GET.get('month', today.month))
        if selected_month < 1 or selected_month > 12:
            selected_month = today.month
    except (ValueError, TypeError):
        selected_month = today.month

    # Call parameterized SQL report query for the logged in user
    report_data = get_monthly_report_data(request.user.id, selected_year, selected_month)

    current_year = today.year
    years_range = list(range(current_year - 4, current_year + 2))
    months_range = [(i, calendar.month_name[i]) for i in range(1, 13)]

    context = {
        'report': report_data,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'years_range': years_range,
        'months_range': months_range,
        'active_page': 'reports'
    }
    return render(request, 'reports/monthly_reports.html', context)


@login_required
def chart_data_api(request):
    """
    JSON API for dynamic Chart.js updates on the dashboard or reports.
    """
    user_id = request.user.id
    trend_data = get_monthly_spending_trend(user_id, 6)
    category_data = get_category_spending_sql(user_id)

    return JsonResponse({
        'trend': trend_data,
        'category': category_data
    })
