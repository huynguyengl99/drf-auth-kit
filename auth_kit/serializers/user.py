"""
User detail serializers for Auth Kit.

This module provides serializers for user profile management
and user detail display.
"""

from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework import serializers

from allauth.account.adapter import (  # pyright: ignore[reportMissingTypeStubs]
    get_adapter,
)

from auth_kit.utils import UserModel


class UserDetailsSerializer(serializers.ModelSerializer[AbstractBaseUser]):
    """User profile information and updates."""

    def validate_username(self, username: str) -> str:
        """
        Validate and clean username using allauth adapter.

        Args:
            username: Username to validate

        Returns:
            Cleaned username
        """

        # Skip uniqueness validation if username belongs to current user
        if self.instance and getattr(self.instance, "username", None) == username:
            return username

        # Use allauth adapter to validate uniqueness for new usernames
        get_adapter().clean_username(username)
        return username

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Metadata configuration for user profile serialization."""

        user_fields = [
            getattr(UserModel, "USERNAME_FIELD", None),
            getattr(UserModel, "EMAIL_FIELD", None),
            "first_name",
            "last_name",
        ]
        extra_fields = [
            field for field in user_fields if field and hasattr(UserModel, field)
        ]
        model = UserModel
        fields = ("pk", *extra_fields)
        read_only_fields = ("email",)
