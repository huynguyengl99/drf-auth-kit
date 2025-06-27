"""
Serializers for social account connection.

This module provides serializers for connecting social accounts
to existing authenticated user accounts.
"""

from typing import Any, cast

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.views import APIView

from allauth.socialaccount.models import (  # pyright: ignore[reportMissingTypeStubs]
    SocialApp,
    SocialLogin,
)

from auth_kit.app_settings import auth_kit_settings

from .login import SocialLoginWithCodeRequestSerializer


class SocialConnectSerializer(SocialLoginWithCodeRequestSerializer):
    """
    Serializer for connecting social accounts to existing user accounts.

    Handles OAuth authorization code exchange and connects the social
    account to the currently authenticated user's account.
    """

    detail = serializers.CharField(read_only=True)

    def check_social_login_account(self, login: SocialLogin) -> None:
        """
        Validate social account before connection.

        Enforces email matching if configured to ensure the social account
        email matches the current user's email address.

        Args:
            login: The SocialLogin instance to validate

        Raises:
            ValidationError: If email validation fails
        """
        email = login.user.email  # pyright: ignore[reportOptionalMemberAccess]
        request = cast(Request, self.context.get("request"))
        user = request.user

        if auth_kit_settings.SOCIAL_CONNECT_REQUIRE_EMAIL_MATCH:
            if getattr(user, "email", None) != email:
                raise serializers.ValidationError(
                    _("Social account email must match your current account email.")
                )

    def get_callback_url(
        self, request: Request, view: APIView, social_app: SocialApp
    ) -> str:
        """
        Get the OAuth callback URL for account connection.

        Args:
            request: The DRF request object
            view: The API view handling the request
            social_app: The social application configuration

        Returns:
            OAuth callback URL for social account connection
        """
        return auth_kit_settings.SOCIAL_CONNECT_CALLBACK_URL_GENERATOR(
            request, view, social_app
        )

    def set_login_user(self, login: SocialLogin) -> None:
        """
        Set the user for the social login to the current authenticated user.

        Args:
            login: The SocialLogin instance to configure
        """
        request = cast(Request, self.context.get("request"))
        user = request.user
        login.user = user

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate the social account connection request.

        Args:
            attrs: Input attributes dictionary

        Returns:
            Dictionary containing success message
        """
        super().validate(attrs)
        return {"detail": _("Connected")}
