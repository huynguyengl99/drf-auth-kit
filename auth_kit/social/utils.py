"""
Utility functions for social authentication.

This module provides helper functions for generating OAuth callback URLs
for social login and account connection workflows.
"""

from django.urls import reverse
from rest_framework.request import Request
from rest_framework.views import APIView

from allauth.socialaccount.models import (  # pyright: ignore[reportMissingTypeStubs]
    SocialApp,
)
from allauth.utils import build_absolute_uri  # pyright: ignore[reportMissingTypeStubs]

from auth_kit.app_settings import auth_kit_settings


def normalize_app_name(social_app: SocialApp) -> tuple[str, str]:
    """
    Normalize social app name into clean app_name and app_slug.

    Args:
        social_app: The social application configuration

    Returns:
        Tuple of (app_name, app_slug) where:
        - app_name: PascalCase name with spaces removed
        - app_slug: lowercase name with dashes converted to underscores
    """
    # Get the base name from available sources
    base_name = (
        social_app.name or social_app.provider_id or social_app.provider.capitalize()
    )

    # Create clean PascalCase name
    app_name = "".join(
        base_name.title().split()  # pyright: ignore[reportUnknownArgumentType]
    )

    # Create lowercase slug
    app_slug = app_name.lower().replace("-", "_")

    return app_name, app_slug


def get_social_login_callback_url(
    request: Request, view: APIView | None, social_app: SocialApp
) -> str:
    """
    Generate OAuth callback URL for social login workflow.

    Args:
        request: The DRF request object
        view: The API view handling the request (optional)
        social_app: The social application configuration

    Returns:
        Complete OAuth callback URL for social login
    """
    callback_url = getattr(view, "callback_url", None) if view else None

    _app_name, app_slug = normalize_app_name(social_app)

    if not callback_url:
        if auth_kit_settings.SOCIAL_LOGIN_CALLBACK_BASE_URL:
            callback_url = (
                f"{auth_kit_settings.SOCIAL_LOGIN_CALLBACK_BASE_URL}/{app_slug}"
            )
        else:
            path = reverse(
                f"{auth_kit_settings.URL_NAMESPACE}rest_social_{app_slug}_login"
            )
            callback_url = build_absolute_uri(request, path)
    return callback_url


def get_social_connect_callback_url(
    request: Request, view: APIView | None, social_app: SocialApp
) -> str:
    """
    Generate OAuth callback URL for social account connection workflow.

    Args:
        request: The DRF request object
        view: The API view handling the request (optional)
        social_app: The social application configuration

    Returns:
        Complete OAuth callback URL for social account connection
    """
    callback_url = getattr(view, "connect_callback_url", None) if view else None

    _app_name, app_slug = normalize_app_name(social_app)

    if not callback_url:
        if auth_kit_settings.SOCIAL_CONNECT_CALLBACK_BASE_URL:
            callback_url = (
                f"{auth_kit_settings.SOCIAL_CONNECT_CALLBACK_BASE_URL}/{app_slug}"
            )
        else:
            path = reverse(
                f"{auth_kit_settings.URL_NAMESPACE}rest_social_{app_slug}_connect"
            )
            callback_url = build_absolute_uri(request, path)
    return callback_url
