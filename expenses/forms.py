from decimal import Decimal
from django import forms
from django.utils import timezone
from .models import Expense, CATEGORY_CHOICES, PAYMENT_METHOD_CHOICES

class ExpenseForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Grocery shopping, Metro card recharge',
            'required': 'required'
        }),
        label='Expense Title'
    )
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01',
            'required': 'required'
        }),
        label='Amount (₹)'
    )
    category = forms.ChoiceField(
        choices=[('', '-- Select Category --')] + CATEGORY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        }),
        label='Category'
    )
    payment_method = forms.ChoiceField(
        choices=[('', '-- Select Payment Method --')] + PAYMENT_METHOD_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        }),
        label='Payment Method'
    )
    expense_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': 'required'
        }),
        label='Expense Date',
        initial=timezone.now
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional details or notes about this expense...'
        }),
        label='Description (Optional)'
    )

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'payment_method', 'expense_date', 'description']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Expense amount must be strictly greater than zero.")
        return amount
