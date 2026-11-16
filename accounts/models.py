from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone

phone_regex = RegexValidator(
    regex=r'^\+?[1-9]\d{9,14}$',
    message="Phone number must be entered in format: '+919876543210' or '9876543210'. Up to 15 digits allowed."
)

class CustomUserManager(BaseUserManager):
    """Custom user manager where phone_number is the unique identifier for auth."""
    def create_user(self, phone_number, full_name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be provided.')
        if not full_name:
            raise ValueError('The Full Name must be provided.')

        # Normalize phone number (strip whitespace and common separators)
        phone_number = str(phone_number).strip().replace(" ", "").replace("-", "")
        extra_fields.setdefault('is_active', True)
        user = self.model(phone_number=phone_number, full_name=full_name.strip(), **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model matching requirement:
    - id: Primary Key
    - full_name: User's complete name
    - phone_number: Unique phone identifier for login
    - password: Securely hashed password
    - date_joined: Account creation timestamp
    - is_active: Whether account is active
    """
    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=150, help_text="Full Name of the user")
    phone_number = models.CharField(
        max_length=17,
        unique=True,
        validators=[phone_regex],
        help_text="Unique phone number used for login and identification"
    )
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"
