from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from expenses.models import Expense
from expenses.sql_queries import get_dashboard_summary, get_monthly_report_data

User = get_user_model()

class ExpenseManagementAndSecurityTests(TestCase):
    """
    Automated test suite covering:
    - Adding expenses
    - Viewing & pagination
    - Searching expenses
    - Updating expenses
    - Deleting expenses
    - SQL Dashboard calculations
    - SQL Monthly report calculations
    - User Data Isolation (User A, User B, User C)
    - Prevention of accessing/modifying another user's expense ID
    - Authentication protection for all protected views
    """

    def setUp(self):
        self.client_a = Client()
        self.client_b = Client()
        self.anon_client = Client()

        # Create User A
        self.user_a = User.objects.create_user(
            phone_number='9876543201',
            full_name='User A',
            password='PasswordA123'
        )

        # Create User B
        self.user_b = User.objects.create_user(
            phone_number='9876543202',
            full_name='User B',
            password='PasswordB123'
        )

        # Log in clients
        self.client_a.force_login(self.user_a)
        self.client_b.force_login(self.user_b)

        # Create Expense for User A
        self.expense_a1 = Expense.objects.create(
            user=self.user_a,
            title='Groceries at Supermarket',
            amount=Decimal('1500.00'),
            category='Food',
            payment_method='UPI',
            expense_date=date.today(),
            description='Weekly grocery replenishment'
        )
        self.expense_a2 = Expense.objects.create(
            user=self.user_a,
            title='Metro Card Recharge',
            amount=Decimal('500.00'),
            category='Transportation',
            payment_method='Debit Card',
            expense_date=date.today(),
            description='Monthly transit pass'
        )

        # Create Expense for User B
        self.expense_b1 = Expense.objects.create(
            user=self.user_b,
            title='Office Lunch',
            amount=Decimal('350.00'),
            category='Food',
            payment_method='Cash',
            expense_date=date.today()
        )

    # 1. Adding an expense
    def test_01_add_expense_success(self):
        """User A adds a new expense; verifies server-side ownership and DB persistence."""
        url = reverse('expense_create')
        payload = {
            'title': 'Electricity Bill',
            'amount': '1250.50',
            'category': 'Bills & Utilities',
            'payment_method': 'Bank Transfer',
            'expense_date': date.today().strftime('%Y-%m-%d'),
            'description': 'Power consumption for the month'
        }
        response = self.client_a.post(url, payload)
        self.assertRedirects(response, reverse('expense_list'))

        # Verify in DB
        expense = Expense.objects.get(title='Electricity Bill')
        self.assertEqual(expense.user, self.user_a)
        self.assertEqual(expense.amount, Decimal('1250.50'))

    # 2. Reject zero or negative amount
    def test_02_add_expense_invalid_amount(self):
        """Test that amounts <= 0 are rejected by the form and model validator."""
        url = reverse('expense_create')
        payload = {
            'title': 'Zero Amount Test',
            'amount': '0.00',
            'category': 'Food',
            'payment_method': 'Cash',
            'expense_date': date.today().strftime('%Y-%m-%d')
        }
        response = self.client_a.post(url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors.get('amount'))

    # 3. Viewing expenses & User Data Isolation
    def test_03_view_expenses_user_data_isolation(self):
        """
        User A must see only User A's expenses (expense_a1, expense_a2).
        User A must NEVER see User B's expenses (expense_b1).
        User B must see only User B's expenses.
        """
        url = reverse('expense_list')

        # Check User A
        response_a = self.client_a.get(url)
        self.assertEqual(response_a.status_code, 200)
        expenses_a_list = response_a.context['page_obj'].object_list
        self.assertIn(self.expense_a1, expenses_a_list)
        self.assertIn(self.expense_a2, expenses_a_list)
        self.assertNotIn(self.expense_b1, expenses_a_list)

        # Check User B
        response_b = self.client_b.get(url)
        self.assertEqual(response_b.status_code, 200)
        expenses_b_list = response_b.context['page_obj'].object_list
        self.assertIn(self.expense_b1, expenses_b_list)
        self.assertNotIn(self.expense_a1, expenses_b_list)
        self.assertNotIn(self.expense_a2, expenses_b_list)

    # 4. Searching expenses
    def test_04_search_expenses(self):
        """User A searches by keyword 'Metro'."""
        url = reverse('expense_list') + '?q=Metro'
        response = self.client_a.get(url)
        self.assertEqual(response.status_code, 200)
        results = response.context['page_obj'].object_list
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, 'Metro Card Recharge')

    # 5. Category filter
    def test_05_filter_by_category(self):
        """User A filters by 'Transportation'."""
        url = reverse('expense_list') + '?category=Transportation'
        response = self.client_a.get(url)
        self.assertEqual(response.status_code, 200)
        results = response.context['page_obj'].object_list
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].category, 'Transportation')

    # 6. Updating own expense
    def test_06_update_own_expense(self):
        """User A updates their own expense."""
        url = reverse('expense_update', kwargs={'pk': self.expense_a1.pk})
        payload = {
            'title': 'Groceries at Supermarket (Updated)',
            'amount': '1750.00',
            'category': 'Food',
            'payment_method': 'UPI',
            'expense_date': self.expense_a1.expense_date.strftime('%Y-%m-%d'),
            'description': 'Updated grocery list'
        }
        response = self.client_a.post(url, payload)
        self.assertRedirects(response, reverse('expense_list'))
        self.expense_a1.refresh_from_db()
        self.assertEqual(self.expense_a1.amount, Decimal('1750.00'))
        self.assertEqual(self.expense_a1.title, 'Groceries at Supermarket (Updated)')

    # 7. Security: User B attempts to update User A's expense
    def test_07_prevent_access_to_another_users_expense_update(self):
        """
        IMPORTANT SECURITY: If User B manually changes the URL ID to User A's expense,
        the backend must return a 404 and reject the update.
        """
        url = reverse('expense_update', kwargs={'pk': self.expense_a1.pk})
        # GET request by User B
        response_get = self.client_b.get(url)
        self.assertEqual(response_get.status_code, 404)

        # POST request by User B attempting tampering
        payload = {
            'title': 'Hacked Title',
            'amount': '9999.00',
            'category': 'Food',
            'payment_method': 'Cash',
            'expense_date': date.today().strftime('%Y-%m-%d')
        }
        response_post = self.client_b.post(url, payload)
        self.assertEqual(response_post.status_code, 404)

        # Verify User A's expense was NOT modified
        self.expense_a1.refresh_from_db()
        self.assertNotEqual(self.expense_a1.title, 'Hacked Title')
        self.assertEqual(self.expense_a1.amount, Decimal('1500.00'))

    # 8. Deleting own expense
    def test_08_delete_own_expense(self):
        """User A deletes their expense."""
        pk = self.expense_a2.pk
        url = reverse('expense_delete', kwargs={'pk': pk})
        response = self.client_a.post(url)
        self.assertRedirects(response, reverse('expense_list'))
        self.assertFalse(Expense.objects.filter(pk=pk).exists())

    # 9. Security: User B attempts to delete User A's expense
    def test_09_prevent_access_to_another_users_expense_delete(self):
        """
        User B attempts to delete User A's expense by manipulating the URL ID.
        Must return 404 and preserve record.
        """
        pk = self.expense_a1.pk
        url = reverse('expense_delete', kwargs={'pk': pk})
        response = self.client_b.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Expense.objects.filter(pk=pk).exists())

    # 10. Dashboard calculations via SQL
    def test_10_dashboard_sql_calculations(self):
        """Test SQL dynamic metrics for User A."""
        metrics = get_dashboard_summary(self.user_a.id)
        # User A has 1500 + 500 = 2000 total, 2 transactions
        self.assertEqual(metrics['total_amount'], Decimal('2000.00'))
        self.assertEqual(metrics['month_amount'], Decimal('2000.00'))
        self.assertEqual(metrics['today_amount'], Decimal('2000.00'))
        self.assertEqual(metrics['total_count'], 2)

        # User B metrics must be completely separate
        metrics_b = get_dashboard_summary(self.user_b.id)
        self.assertEqual(metrics_b['total_amount'], Decimal('350.00'))
        self.assertEqual(metrics_b['total_count'], 1)

    # 11. Monthly report calculations via SQL
    def test_11_monthly_report_sql_calculations(self):
        """Test SQL monthly report for current month."""
        today = date.today()
        report = get_monthly_report_data(self.user_a.id, today.year, today.month)
        self.assertEqual(report['current_month_total'], Decimal('2000.00'))
        self.assertEqual(report['current_month_count'], 2)
        # Category breakdown: Food (1500) and Transportation (500)
        self.assertEqual(len(report['category_breakdown']), 2)

    # 12. Authentication protection
    def test_12_authentication_protection(self):
        """Unauthenticated requests to private URLs must redirect to login."""
        protected_urls = [
            reverse('dashboard'),
            reverse('expense_list'),
            reverse('expense_create'),
            reverse('monthly_reports'),
            reverse('settings'),
        ]
        login_url = reverse('login')
        for url in protected_urls:
            response = self.anon_client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(login_url, response.url)
