"""
User registration serializers for Auth Kit.

This module provides serializers for user registration, email verification,
and email verification resend functionality with django-allauth integration.
"""

# pyright: reportUnknownMemberType=false
from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from allauth.account.adapter import (  # pyright: ignore[reportMissingTypeStubs]
    get_adapter,  # pyright: ignore[reportUnknownVariableType]
)
from allauth.account.models import (  # pyright: ignore[reportMissingTypeStubs]
    EmailAddress,
)
from allauth.account.utils import (  # pyright: ignore[reportMissingTypeStubs]
    setup_user_email,  # pyright: ignore[reportUnknownVariableType]
)

from auth_kit.serializer_fields import UnquoteStringField
from auth_kit.serializers.login_factors import UserNameField


class RegisterSerializer(serializers.Serializer[dict[str, Any]]):
    """User registration with email verification."""

    if UserNameField == "username":
        username = serializers.CharField(write_only=True)

    email = serializers.EmailField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    detail = serializers.CharField(read_only=True)

    def validate_username(self, username: str) -> str:
        """
        Validate and clean username.

        Args:
            username: Username to validate

        Returns:
            Cleaned username
        """
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email: str) -> str:
        """
        Validate and clean email address.

        Args:
            email: Email address to validate

        Returns:
            Cleaned email address

        Raises:
            ValidationError: If email is already registered
        """
        email = get_adapter().clean_email(email)
        if EmailAddress.objects.filter(email=email).exists():
            raise ValidationError(
                _("A user is already registered with this e-mail address.")
            )
        return email

    def validate_password1(self, password: str) -> str:
        """
        Validate and clean password.

        Args:
            password: Password to validate

        Returns:
            Cleaned password
        """
        return str(get_adapter().clean_password(password))

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate registration data including password confirmation.

        Args:
            attrs: Input attributes dictionary

        Returns:
            Validated attributes

        Raises:
            ValidationError: If passwords don't match
        """
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )
        return attrs

    def custom_signup(self, request: Request, user: AbstractBaseUser) -> None:
        """
        Perform custom signup logic.

        Override this method to add custom registration logic.

        Args:
            request: The HTTP request object
            user: The newly created user instance
        """
        pass

    def get_cleaned_data(self) -> dict[str, Any]:
        """
        Get cleaned registration data.

        Returns:
            Dictionary of cleaned registration data
        """
        return {
            "username": self.validated_data.get("username", ""),
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
        }

    def save(self, **kwargs: Any) -> AbstractBaseUser:  # type: ignore[override]
        """
        Save the new user account.

        Args:
            **kwargs: Additional keyword arguments

        Returns:
            The newly created user instance

        Raises:
            ValidationError: If password validation fails
        """
        request = self.context["request"]
        adapter = get_adapter()
        user: AbstractBaseUser = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()

        user = adapter.save_user(request, user, self, commit=False)
        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data["password1"], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                ) from exc
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class VerifyEmailSerializer(serializers.Serializer[dict[str, Any]]):
    """Email address verification with confirmation key."""

    key = UnquoteStringField(required=True, write_only=True)
    detail = serializers.CharField(read_only=True)


class ResendEmailVerificationSerializer(serializers.Serializer[dict[str, Any]]):
    """Request new email verification message."""

    email = serializers.EmailField(required=True, write_only=True)
    detail = serializers.CharField(read_only=True)
