from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsAuthenticationTests(TestCase):
    """
    Automated test suite covering:
    - User registration
    - Duplicate phone number prevention
    - Phone number validation
    - Password hashing
    - Valid & invalid login
    - User profile and settings
    - Password change with verification
    - Logout
    """

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.settings_url = reverse('settings')
        self.dashboard_url = reverse('dashboard')

        # Existing user for tests
        self.existing_user = User.objects.create_user(
            phone_number='9876543210',
            full_name='Existing User',
            password='SecurePassword123'
        )

    def test_01_user_registration_success(self):
        """Test registering a new user with valid phone and password."""
        payload = {
            'full_name': 'New Registered User',
            'phone_number': '9876543211',
            'password': 'StrongPassword123',
            'confirm_password': 'StrongPassword123'
        }
        response = self.client.post(self.register_url, payload)
        # Should redirect to login page with success message
        self.assertRedirects(response, self.login_url)

        # Verify user exists in database
        user = User.objects.get(phone_number='9876543211')
        self.assertEqual(user.full_name, 'New Registered User')
        # Verify password is secure hash, NOT plain text
        self.assertTrue(user.check_password('StrongPassword123'))
        self.assertNotEqual(user.password, 'StrongPassword123')

    def test_02_duplicate_phone_number_prevention(self):
        """Test that registering an existing phone number is strictly rejected."""
        payload = {
            'full_name': 'Another User',
            'phone_number': '9876543210',  # already registered
            'password': 'AnotherPassword123',
            'confirm_password': 'AnotherPassword123'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, 200)
        # Form should contain validation error
        self.assertFormError(
            response.context['form'],
            'phone_number',
            'An account with this phone number is already registered. Please log in.'
        )

    def test_03_phone_number_format_validation(self):
        """Test that invalid phone formats are rejected."""
        invalid_numbers = ['1234', 'abcdefghij', '12345678901234567890']
        for bad_phone in invalid_numbers:
            payload = {
                'full_name': 'Bad Phone User',
                'phone_number': bad_phone,
                'password': 'ValidPassword123',
                'confirm_password': 'ValidPassword123'
            }
            response = self.client.post(self.register_url, payload)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['form'].errors.get('phone_number'))

    def test_04_password_mismatch_validation(self):
        """Test registration when password and confirm_password do not match."""
        payload = {
            'full_name': 'Mismatch User',
            'phone_number': '9876543212',
            'password': 'PasswordOne123',
            'confirm_password': 'PasswordTwo123'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'confirm_password',
            'Passwords do not match. Please re-enter carefully.'
        )

    def test_05_valid_login(self):
        """Test login with valid phone number and password."""
        payload = {
            'phone_number': '9876543210',
            'password': 'SecurePassword123'
        }
        response = self.client.post(self.login_url, payload)
        self.assertRedirects(response, self.dashboard_url)
        # Check session user
        self.assertEqual(int(self.client.session['_auth_user_id']), self.existing_user.id)

    def test_06_invalid_login(self):
        """Test login with incorrect credentials."""
        payload = {
            'phone_number': '9876543210',
            'password': 'WrongPassword999'
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].non_field_errors())

    def test_07_profile_update_full_name(self):
        """Test user updating their full name from settings."""
        self.client.force_login(self.existing_user)
        payload = {
            'action': 'update_profile',
            'full_name': 'Updated Name User'
        }
        response = self.client.post(self.settings_url, payload)
        self.assertRedirects(response, self.settings_url)
        self.existing_user.refresh_from_db()
        self.assertEqual(self.existing_user.full_name, 'Updated Name User')

    def test_08_change_password_with_current_verification(self):
        """Test password change requires valid current password."""
        self.client.force_login(self.existing_user)

        # 1. Incorrect current password
        bad_payload = {
            'action': 'change_password',
            'current_password': 'WrongCurrentPassword',
            'new_password': 'BrandNewPassword123',
            'confirm_new_password': 'BrandNewPassword123'
        }
        bad_resp = self.client.post(self.settings_url, bad_payload)
        self.assertEqual(bad_resp.status_code, 200)
        self.existing_user.refresh_from_db()
        self.assertFalse(self.existing_user.check_password('BrandNewPassword123'))

        # 2. Correct current password
        good_payload = {
            'action': 'change_password',
            'current_password': 'SecurePassword123',
            'new_password': 'BrandNewPassword123',
            'confirm_new_password': 'BrandNewPassword123'
        }
        good_resp = self.client.post(self.settings_url, good_payload)
        self.assertRedirects(good_resp, self.settings_url)
        self.existing_user.refresh_from_db()
        self.assertTrue(self.existing_user.check_password('BrandNewPassword123'))

    def test_09_logout(self):
        """Test logout clears session."""
        self.client.force_login(self.existing_user)
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.login_url)
        self.assertNotIn('_auth_user_id', self.client.session)
