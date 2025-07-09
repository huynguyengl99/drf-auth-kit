"""
User registration serializers for Auth Kit.

This module provides serializers for user registration, email verification,
and email verification resend functionality with django-allauth integration.
"""

from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.request import Request

from allauth.account.adapter import (  # pyright: ignore[reportMissingTypeStubs]
    get_adapter,
)
from allauth.account.models import (  # pyright: ignore[reportMissingTypeStubs]
    EmailAddress,
)
from allauth.account.utils import (  # pyright: ignore[reportMissingTypeStubs]
    setup_user_email,
)

from auth_kit.serializer_fields import UnquoteStringField
from auth_kit.utils import UserModel, UserNameField


class RegisterSerializer(serializers.Serializer[dict[str, Any]]):
    """User registration with email verification."""

    username = serializers.CharField(write_only=True)

    email = serializers.EmailField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    detail = serializers.CharField(read_only=True)
    first_name = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize login serializer.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        super().__init__(*args, **kwargs)

        if UserNameField == "username":
            pass
        elif UserNameField == "email" or not UserNameField:
            self.fields.pop("username")
        else:
            self.fields.pop("username")
            self.fields[UserNameField] = serializers.CharField(write_only=True)

        if not hasattr(UserModel, "first_name"):
            self.fields.pop("first_name")

        if not hasattr(UserModel, "last_name"):
            self.fields.pop("last_name")

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
            "username": self.validated_data.get(UserNameField, ""),
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
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class VerifyEmailSerializer(serializers.Serializer[dict[str, Any]]):
    """Email address verification with confirmation key."""

    key = UnquoteStringField(required=True, write_only=True, default=empty)
    detail = serializers.CharField(read_only=True)


class ResendEmailVerificationSerializer(serializers.Serializer[dict[str, Any]]):
    """Request new email verification message."""

    email = serializers.EmailField(required=True, write_only=True)
    detail = serializers.CharField(read_only=True)
