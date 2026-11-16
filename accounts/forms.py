import re
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'autocomplete': 'name',
            'required': 'required'
        }),
        label='Full Name'
    )
    phone_number = forms.CharField(
        max_length=17,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 9876543210 or +919876543210',
            'autocomplete': 'tel',
            'required': 'required'
        }),
        label='Phone Number'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a secure password (min. 6 characters)',
            'autocomplete': 'new-password',
            'required': 'required'
        }),
        label='Password',
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
            'required': 'required'
        }),
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ['full_name', 'phone_number']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '').strip().replace(" ", "").replace("-", "")
        # Validate format: 10 to 15 digits, optional leading +
        if not re.match(r'^\+?[1-9]\d{9,14}$', phone_number):
            raise ValidationError("Please enter a valid phone number with 10 to 15 digits (e.g. 9876543210 or +919876543210).")
        
        # Check uniqueness
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("An account with this phone number is already registered. Please log in.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match. Please re-enter carefully.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone_number = self.cleaned_data['phone_number']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    phone_number = forms.CharField(
        max_length=17,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter registered phone number',
            'autocomplete': 'tel',
            'required': 'required'
        }),
        label='Phone Number'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
            'required': 'required'
        }),
        label='Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number', '').strip().replace(" ", "").replace("-", "")
        password = cleaned_data.get('password')

        if phone_number and password:
            self.user_cache = authenticate(phone_number=phone_number, password=password)
            if self.user_cache is None:
                raise ValidationError("Invalid phone number or password. Please check your credentials.")
            elif not self.user_cache.is_active:
                raise ValidationError("This user account is inactive.")
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)


class UserProfileUpdateForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Update full name'
        }),
        label='Full Name'
    )

    class Meta:
        model = User
        fields = ['full_name']


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password'
        }),
        label='Current Password',
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password (min. 6 characters)'
        }),
        label='New Password',
        min_length=6,
        required=True
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        label='Confirm New Password',
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError("Current password is incorrect.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                self.add_error('confirm_new_password', "New passwords do not match.")
        return cleaned_data

    def save(self):
        new_password = self.cleaned_data.get('new_password')
        self.user.set_password(new_password)
        self.user.save()
        return self.user
