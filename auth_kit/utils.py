"""
Utility functions for Auth Kit.

This module provides helper functions for JWT token generation,
security decorators, and type casting utilities.
"""

from typing import Any, cast

from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


def jwt_encode(user: AbstractBaseUser) -> tuple[AccessToken, RefreshToken]:
    """
    Generate JWT access and refresh tokens for a user.

    Args:
        user: The user to generate tokens for

    Returns:
        Tuple containing (access_token, refresh_token)
    """
    from auth_kit.app_settings import auth_kit_settings

    refresh: RefreshToken = auth_kit_settings.JWT_TOKEN_CLAIMS_SERIALIZER.get_token(user)  # type: ignore
    return refresh.access_token, refresh


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        "password",
        "old_password",
        "new_password1",
        "new_password2",
        "password1",
        "password2",
    ),
)


def cast_dict(arg: Any) -> dict[str, Any]:
    """
    Cast an argument to a dictionary type.

    Args:
        arg: The argument to cast

    Returns:
        The argument cast as a dictionary
    """
    return cast(dict[str, Any], arg)
