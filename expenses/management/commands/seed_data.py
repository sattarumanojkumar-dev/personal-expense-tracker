from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from expenses.models import Expense

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds database with User A, User B, and User C with distinct expenses for testing isolation.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding multi-user sample data...")

        # 1. User A
        user_a, created = User.objects.get_or_create(
            phone_number='9876543201',
            defaults={'full_name': 'User A (Aarav Sharma)'}
        )
        if created:
            user_a.set_password('Password123')
            user_a.save()
        self.stdout.write(f"User A ready: {user_a.phone_number} / Password123")

        # 2. User B
        user_b, created = User.objects.get_or_create(
            phone_number='9876543202',
            defaults={'full_name': 'User B (Bhavya Patel)'}
        )
        if created:
            user_b.set_password('Password123')
            user_b.save()
        self.stdout.write(f"User B ready: {user_b.phone_number} / Password123")

        # 3. User C
        user_c, created = User.objects.get_or_create(
            phone_number='9876543203',
            defaults={'full_name': 'User C (Chetan Verma)'}
        )
        if created:
            user_c.set_password('Password123')
            user_c.save()
        self.stdout.write(f"User C ready: {user_c.phone_number} / Password123")

        # Create Admin
        admin_user, created = User.objects.get_or_create(
            phone_number='9999999999',
            defaults={
                'full_name': 'System Administrator',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('AdminPassword123')
            admin_user.save()
        self.stdout.write(f"Admin ready: {admin_user.phone_number} / AdminPassword123")

        # Clear existing expenses for seed idempotence
        Expense.objects.filter(user__in=[user_a, user_b, user_c]).delete()

        today = date.today()

        # Seed User A Expenses
        expenses_a = [
            {'title': 'Weekly Organic Grocery', 'amount': Decimal('2450.00'), 'category': 'Food', 'payment_method': 'UPI', 'date': today, 'desc': 'Fresh vegetables and dairy'},
            {'title': 'Electricity & Power Bill', 'amount': Decimal('1850.50'), 'category': 'Bills & Utilities', 'payment_method': 'Bank Transfer', 'date': today - timedelta(days=2), 'desc': 'Monthly state electricity'},
            {'title': 'Fuel for Car', 'amount': Decimal('3200.00'), 'category': 'Transportation', 'payment_method': 'Credit Card', 'date': today - timedelta(days=4), 'desc': 'Full tank HP Petrol'},
            {'title': 'Weekend Movie & Dinner', 'amount': Decimal('1650.00'), 'category': 'Entertainment', 'payment_method': 'UPI', 'date': today - timedelta(days=7), 'desc': 'Cinema tickets and snacks'},
            {'title': 'Online Python Course', 'amount': Decimal('2999.00'), 'category': 'Education', 'payment_method': 'Debit Card', 'date': today - timedelta(days=12), 'desc': 'Django web development course'},
            {'title': 'Medical Checkup & Pharmacy', 'amount': Decimal('1450.00'), 'category': 'Healthcare', 'payment_method': 'UPI', 'date': today - timedelta(days=18), 'desc': 'Routine health examination'},
            {'title': 'Flight Tickets to Mumbai', 'amount': Decimal('7800.00'), 'category': 'Travel', 'payment_method': 'Credit Card', 'date': today - timedelta(days=35), 'desc': 'Client meeting flight'},
            {'title': 'Amazon Clothing Order', 'amount': Decimal('4200.00'), 'category': 'Shopping', 'payment_method': 'Credit Card', 'date': today - timedelta(days=40), 'desc': 'Formal shirts and trousers'},
        ]
        for item in expenses_a:
            Expense.objects.create(
                user=user_a,
                title=item['title'],
                amount=item['amount'],
                category=item['category'],
                payment_method=item['payment_method'],
                expense_date=item['date'],
                description=item['desc']
            )

        # Seed User B Expenses (Completely different data)
        expenses_b = [
            {'title': 'Cafeteria Coffee & Breakfast', 'amount': Decimal('180.00'), 'category': 'Food', 'payment_method': 'Cash', 'date': today, 'desc': 'Daily office breakfast'},
            {'title': 'Metro Smart Card Recharge', 'amount': Decimal('800.00'), 'category': 'Transportation', 'payment_method': 'UPI', 'date': today - timedelta(days=3), 'desc': 'Commute pass'},
            {'title': 'Mobile Broadband Plan', 'amount': Decimal('999.00'), 'category': 'Bills & Utilities', 'payment_method': 'UPI', 'date': today - timedelta(days=5), 'desc': 'Jio Fiber unlimited'},
            {'title': 'Casual Sneakers', 'amount': Decimal('2890.00'), 'category': 'Shopping', 'payment_method': 'Debit Card', 'date': today - timedelta(days=15), 'desc': 'Puma running shoes'},
        ]
        for item in expenses_b:
            Expense.objects.create(
                user=user_b,
                title=item['title'],
                amount=item['amount'],
                category=item['category'],
                payment_method=item['payment_method'],
                expense_date=item['date'],
                description=item['desc']
            )

        # Seed User C Expenses (Completely different data)
        expenses_c = [
            {'title': 'Textbooks and Reference Manuals', 'amount': Decimal('1200.00'), 'category': 'Education', 'payment_method': 'UPI', 'date': today, 'desc': 'University semester books'},
            {'title': 'Hostel Mess Fee', 'amount': Decimal('4500.00'), 'category': 'Food', 'payment_method': 'Bank Transfer', 'date': today - timedelta(days=8), 'desc': 'Monthly mess subscription'},
            {'title': 'Train Ticket to Home', 'amount': Decimal('650.00'), 'category': 'Travel', 'payment_method': 'UPI', 'date': today - timedelta(days=22), 'desc': 'Diwali vacation journey'},
        ]
        for item in expenses_c:
            Expense.objects.create(
                user=user_c,
                title=item['title'],
                amount=item['amount'],
                category=item['category'],
                payment_method=item['payment_method'],
                expense_date=item['date'],
                description=item['desc']
            )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with Users A, B, C!"))
