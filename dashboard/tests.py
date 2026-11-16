from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from expenses.models import Expense

User = get_user_model()

class DashboardViewTests(TestCase):
    """
    Test suite for Dashboard views and Chart APIs:
    - Verifies dashboard authentication requirement
    - Verifies dynamic SQL-calculated metric cards
    - Verifies user isolation on the dashboard
    - Verifies Chart.js JSON API response
    """

    def setUp(self):
        self.client_a = Client()
        self.client_b = Client()
        self.anon_client = Client()

        self.user_a = User.objects.create_user(
            phone_number='9876543301',
            full_name='User A Alpha',
            password='Password123'
        )
        self.user_b = User.objects.create_user(
            phone_number='9876543302',
            full_name='User B Beta',
            password='Password123'
        )

        self.client_a.force_login(self.user_a)
        self.client_b.force_login(self.user_b)

        # Create expense for User A
        self.exp_a = Expense.objects.create(
            user=self.user_a,
            title='Alpha Spending',
            amount=Decimal('850.00'),
            category='Shopping',
            payment_method='UPI',
            expense_date=date.today()
        )

        # Create expense for User B
        self.exp_b = Expense.objects.create(
            user=self.user_b,
            title='Beta Spending',
            amount=Decimal('420.00'),
            category='Food',
            payment_method='Cash',
            expense_date=date.today()
        )

    def test_dashboard_unauthenticated_redirect(self):
        """Unauthenticated user accessing dashboard is redirected to login."""
        response = self.anon_client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_authenticated_success_and_isolation(self):
        """User A sees only User A metrics and transactions on their dashboard."""
        response = self.client_a.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # Verify context data
        summary = response.context['summary']
        self.assertEqual(summary['total_amount'], Decimal('850.00'))
        self.assertEqual(summary['total_count'], 1)

        recent = response.context['recent_transactions']
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]['title'], 'Alpha Spending')
        self.assertNotEqual(recent[0]['title'], 'Beta Spending')

    def test_dashboard_chart_data_api(self):
        """Test chart JSON API returns user-specific trend and category metrics."""
        url = reverse('chart_data_api')
        response = self.client_a.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('trend', data)
        self.assertIn('category', data)
        self.assertIn('Shopping', data['category']['categories'])
        self.assertNotIn('Food', data['category']['categories'])  # Food belongs to User B
