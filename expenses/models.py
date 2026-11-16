from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

CATEGORY_CHOICES = [
    ('Food', 'Food'),
    ('Transportation', 'Transportation'),
    ('Shopping', 'Shopping'),
    ('Education', 'Education'),
    ('Entertainment', 'Entertainment'),
    ('Healthcare', 'Healthcare'),
    ('Bills & Utilities', 'Bills & Utilities'),
    ('Travel', 'Travel'),
    ('Other', 'Other'),
]

PAYMENT_METHOD_CHOICES = [
    ('Cash', 'Cash'),
    ('UPI', 'UPI'),
    ('Debit Card', 'Debit Card'),
    ('Credit Card', 'Credit Card'),
    ('Bank Transfer', 'Bank Transfer'),
    ('Other', 'Other'),
]

class Expense(models.Model):
    """
    Expense model mapping to Table 2: Expenses
    - id: Primary Key
    - user: Foreign Key referencing Users
    - title: Short expense title
    - amount: Numeric value in INR (greater than 0)
    - category: Category selection
    - payment_method: Payment method selection
    - expense_date: Date of expense
    - description: Optional additional note
    - created_at: Creation timestamp
    - updated_at: Last modification timestamp
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses',
        db_index=True
    )
    title = models.CharField(max_length=200, help_text="Expense title or item name")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message="Amount must be greater than zero.")],
        help_text="Expense amount in Indian Rupees (₹)"
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    expense_date = models.DateField(default=timezone.now, db_index=True)
    description = models.TextField(blank=True, null=True, help_text="Optional description or notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expenses'
        ordering = ['-expense_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'expense_date'], name='idx_exp_user_date'),
            models.Index(fields=['user', 'category'], name='idx_exp_user_cat'),
        ]

    def __str__(self):
        return f"{self.title} - ₹{self.amount} ({self.category})"
