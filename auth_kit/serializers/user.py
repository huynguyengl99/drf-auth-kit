"""
User detail serializers for Auth Kit.

This module provides serializers for user profile management
and user detail display.
"""

from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework import serializers

from allauth.account.adapter import (  # pyright: ignore[reportMissingTypeStubs]
    get_adapter,  # pyright: ignore[reportUnknownVariableType]
)

from auth_kit.serializers.login_factors import UserModel


class UserDetailsSerializer(serializers.ModelSerializer[AbstractBaseUser]):
    """User profile information and updates."""

    @staticmethod
    def validate_username(username: str) -> str:
        """
        Validate and clean username using allauth adapter.

        Args:
            username: Username to validate

        Returns:
            Cleaned username
        """
        username = get_adapter().clean_username(username)  # pyright: ignore
        return username

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Metadata configuration for user profile serialization."""

        extra_fields: list[str] = []
        if hasattr(UserModel, "USERNAME_FIELD"):
            extra_fields.append(UserModel.USERNAME_FIELD)
        if hasattr(UserModel, "EMAIL_FIELD"):
            extra_fields.append(UserModel.EMAIL_FIELD)
        if hasattr(UserModel, "first_name"):
            extra_fields.append("first_name")
        if hasattr(UserModel, "last_name"):
            extra_fields.append("last_name")
        model = UserModel
        fields = ("pk", *extra_fields)
        read_only_fields = ("email",)
