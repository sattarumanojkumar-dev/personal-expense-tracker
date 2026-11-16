from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class PhoneNumberBackend(BaseBackend):
    """
    Authenticate users using their phone number and password.
    """
    def authenticate(self, request, phone_number=None, password=None, **kwargs):
        if phone_number is None:
            phone_number = kwargs.get('username')
        if not phone_number or not password:
            return None

        # Clean/normalize phone number
        phone_number = str(phone_number).strip().replace(" ", "").replace("-", "")

        try:
            user = User.objects.get(phone_number=phone_number)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            # Run the default password hasher once to prevent timing attacks
            User().set_password(password)
            return None
        return None

    def user_can_authenticate(self, user):
        return getattr(user, 'is_active', True)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
