# accounts/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"


account_activation_token = AccountActivationTokenGenerator()
