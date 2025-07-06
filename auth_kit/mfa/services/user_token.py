"""
Ephemeral token service for MFA authentication flow.

This module provides secure token generation and validation for
maintaining state between MFA authentication steps while preventing
replay attacks and ensuring time-limited validity.
"""

from datetime import datetime
from typing import Any, cast

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36

from auth_kit.mfa.mfa_settings import auth_kit_mfa_settings


class EphemeralTokenService:
    """
    Service for managing ephemeral tokens in MFA authentication flow.

    Provides secure token generation and validation with time-based expiry
    and user/method binding to prevent token misuse and replay attacks.

    Class Attributes:
        KEY_SALT: Salt for HMAC token generation
        SECRET: Secret key for token signing
        EXPIRY_TIME: Token validity duration in seconds
    """

    KEY_SALT = "auth_kit.mfa.utils.UserTokenGenerator"
    SECRET = settings.SECRET_KEY
    EXPIRY_TIME = auth_kit_mfa_settings.MFA_EPHEMERAL_TOKEN_EXPIRY

    def make_token(self, user: User, mfa_method_name: str) -> str:
        """
        Generate ephemeral token for user and MFA method.

        Creates a time-limited token that binds user identity with
        specific MFA method for secure state management.

        Args:
            user: User instance for token generation
            mfa_method_name: MFA method name to bind to token

        Returns:
            Signed ephemeral token string
        """
        return self._make_token_with_timestamp(
            user, mfa_method_name, int(datetime.now().timestamp())
        )

    def check_token(self, token: str) -> tuple[User, str] | None:
        """
        Validate and decode ephemeral token.

        Verifies token signature, expiry time, and extracts user
        and method information from valid tokens.

        Args:
            token: Ephemeral token string to validate

        Returns:
            Tuple of (user, method_name) if valid, None if invalid
        """
        user_model = cast(User, get_user_model())
        try:
            token = str(token)
            user_pk, mfa_method_name, ts_b36, _token_hash = token.rsplit("-", 3)
            ts = base36_to_int(ts_b36)
            user = user_model.objects.get(pk=user_pk)
        except (ValueError, TypeError, user_model.DoesNotExist):
            return None

        if (datetime.now().timestamp() - ts) > self.EXPIRY_TIME:
            return None  # pragma: no cover

        if not constant_time_compare(
            self._make_token_with_timestamp(user, mfa_method_name, ts), token
        ):
            return None  # pragma: no cover

        return user, mfa_method_name

    def _make_hash_value(self, user: User, mfa_method_name: str, timestamp: int) -> str:
        """
        Create hash value for token generation.

        Combines user identity, method name, and timestamp into
        a string for HMAC signing.

        Args:
            user: User instance
            mfa_method_name: MFA method name
            timestamp: Unix timestamp

        Returns:
            Hash value string for token signing
        """
        email_field = user.get_email_field_name()
        email = getattr(user, email_field, "") or ""
        return f"{user.pk}:{timestamp}:{email}:{mfa_method_name}"

    def _make_token_with_timestamp(
        self, user: User, mfa_method_name: str, timestamp: int, **kwargs: Any
    ) -> str:
        """
        Generate token with specific timestamp.

        Creates signed token with user data, method name, and timestamp
        for secure authentication state management.

        Args:
            user: User instance
            mfa_method_name: MFA method name
            timestamp: Unix timestamp for token generation
            **kwargs: Additional arguments (unused)

        Returns:
            Signed token string with format: user_pk-method_name-timestamp-hash
        """
        ts_b36 = int_to_base36(timestamp)
        token_hash = salted_hmac(
            self.KEY_SALT,
            self._make_hash_value(user, mfa_method_name, timestamp),
            secret=self.SECRET,
        ).hexdigest()
        return f"{user.pk}-{mfa_method_name}-{ts_b36}-{token_hash}"


ephemeral_token_service = EphemeralTokenService()
