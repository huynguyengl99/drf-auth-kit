"""
Core authentication serializers for Auth Kit.

This module provides base serializers for login request/response handling,
user authentication, and token generation for different authentication types.
"""

from typing import Any, cast

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.serializers import Serializer

from allauth.account import (  # pyright: ignore[reportMissingTypeStubs]
    app_settings as allauth_account_settings,
)
from allauth.account.models import (  # pyright: ignore[reportMissingTypeStubs]
    EmailAddress,
)
from drf_spectacular.utils import (
    extend_schema_field,  # pyright: ignore[reportUnknownVariableType]
)
from rest_framework_simplejwt.settings import api_settings as jwt_settings

from auth_kit.app_settings import auth_kit_settings
from auth_kit.serializers import JWTSerializer
from auth_kit.serializers.token import TokenSerializer
from auth_kit.utils import cast_dict, jwt_encode

UserModel: type[User] = get_user_model()  # type: ignore[assignment, unused-ignore]
UserNameField: str = UserModel.USERNAME_FIELD


class LoginRequestSerializer(serializers.Serializer[dict[str, Any]]):
    """User authentication credentials."""

    if UserNameField == "username":
        username = serializers.CharField(write_only=True)
    elif UserNameField == "email":
        email = serializers.EmailField(write_only=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    def authenticate(self, **kwargs: Any) -> AbstractBaseUser | None:
        """
        Authenticate user with provided credentials.

        Args:
            **kwargs: Authentication credentials

        Returns:
            Authenticated user instance or None
        """
        return authenticate(self.context["request"], **kwargs)

    def get_auth_user(
        self, username: str | None, email: str | None, password: str | None
    ) -> AbstractBaseUser | None:
        """
        Get authenticated user based on username/email and password.

        Args:
            username: Username for authentication
            email: Email for authentication
            password: Password for authentication

        Returns:
            Authenticated user instance or None
        """
        # Authentication through email
        if UserModel.USERNAME_FIELD == "email":
            return self.authenticate(email=email, password=password)
        elif UserModel.USERNAME_FIELD == "username":
            return self.authenticate(username=username, password=password)
        else:
            return None

    @staticmethod
    def validate_auth_user_status(user: AbstractBaseUser | None) -> None:
        """
        Validate that the authenticated user is active.

        Args:
            user: User instance to validate

        Raises:
            ValidationError: If user account is disabled
        """
        if user and not user.is_active:
            msg = _("User account is disabled.")
            raise exceptions.ValidationError(msg)

    def validate_email_verification_status(self, user: AbstractBaseUser) -> None:
        """
        Validate email verification status when required.

        Args:
            user: User instance to validate

        Raises:
            ValidationError: If email verification is mandatory but not completed
        """
        user_email_queryset = cast(
            QuerySet[EmailAddress],
            user.emailaddress_set,  # type: ignore
        )
        user_email: str = user.email  # type: ignore
        if (
            allauth_account_settings.EMAIL_VERIFICATION
            == allauth_account_settings.EmailVerificationMethod.MANDATORY
            and not user_email_queryset.filter(
                email=user_email,
                verified=True,
            ).exists()
        ):
            raise serializers.ValidationError(_("E-mail is not verified."))

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate login credentials and user status.

        Args:
            attrs: Input attributes dictionary

        Returns:
            Validated attributes with user in context

        Raises:
            ValidationError: If authentication fails or user is inactive
        """
        super().validate(attrs)
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")
        user = self.get_auth_user(username, email, password)

        if not user:
            msg = _("Unable to log in with provided credentials.")
            raise exceptions.ValidationError(msg)

        # Did we get back an active user?
        self.validate_auth_user_status(user)

        # If required, is the email verified?
        self.validate_email_verification_status(user)

        self.context["user"] = user
        return attrs


class BaseLoginResponseSerializer(serializers.Serializer[dict[str, Any]]):
    """Authentication response with user details."""

    user = serializers.SerializerMethodField()

    @extend_schema_field(auth_kit_settings.USER_DETAILS_SERIALIZER)
    def get_user(self, obj: dict[str, Any]) -> dict[str, Any]:
        """
        Get serialized user details for the response.

        Args:
            obj: Object containing user data

        Returns:
            Serialized user data dictionary
        """
        user_detail_serializer = auth_kit_settings.USER_DETAILS_SERIALIZER(
            obj["user"], context=self.context
        )
        return cast_dict(
            user_detail_serializer.data  # pyright: ignore[reportUnknownMemberType]
        )


class JWTResponseSerializer(JWTSerializer, BaseLoginResponseSerializer):
    """JWT authentication tokens and user information."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Generate JWT tokens for authenticated user.

        Args:
            attrs: Input attributes dictionary

        Returns:
            Dictionary containing user data and JWT tokens
        """
        super().validate(attrs)
        user = self.context["user"]
        access_token_expiration = timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME
        refresh_token_expiration = timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME

        access_token, refresh_token = jwt_encode(user)

        data = {
            "user": user,
            "access": access_token,
            "refresh": refresh_token,
            "access_expiration": access_token_expiration,
            "refresh_expiration": refresh_token_expiration,
        }

        return data


class TokenResponseSerializer(TokenSerializer, BaseLoginResponseSerializer):
    """DRF token authentication and user information."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Get or create DRF token for authenticated user.

        Args:
            attrs: Input attributes dictionary

        Returns:
            Dictionary containing user data and authentication token
        """
        super().validate(attrs)
        user = self.context["user"]
        token, _ = auth_kit_settings.AUTH_TOKEN_MODEL.objects.get_or_create(user=user)

        return {
            "user": user,
            "key": token.key,  # pyright: ignore[reportUnknownMemberType]
        }


def get_login_response_serializer() -> type[Serializer[dict[str, Any]]]:
    """
    Get the appropriate login response serializer based on current settings.

    Returns:
        The appropriate response serializer class
    """
    if auth_kit_settings.LOGIN_RESPONSE_SERIALIZER != BaseLoginResponseSerializer:
        return auth_kit_settings.LOGIN_RESPONSE_SERIALIZER

    if auth_kit_settings.AUTH_TYPE == "jwt":
        return JWTResponseSerializer
    elif auth_kit_settings.AUTH_TYPE == "token":
        return TokenResponseSerializer
    else:
        raise TypeError(
            "You must specify your login response serializer via  auth_kit_settings.LOGIN_RESPONSE_SERIALIZER"
        )
