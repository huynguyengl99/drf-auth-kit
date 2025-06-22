"""
Login serializer for Auth Kit.

This module provides the main login serializer factory that combines
request and response serialization functionality based on current settings.
"""

from functools import lru_cache
from typing import Any

from rest_framework.serializers import Serializer

from auth_kit.app_settings import auth_kit_settings
from auth_kit.serializers.login_factors import (
    get_login_response_serializer,
)


@lru_cache
def get_login_serializer() -> type[Serializer[dict[str, Any]]]:
    """
    Get the login serializer class based on current settings.

    This function creates the serializer class dynamically by combining
    the appropriate request and response serializers based on current
    auth kit settings.

    Returns:
        The combined login serializer class
    """

    # Get the serializer classes based on current settings
    response_serializer = get_login_response_serializer()

    # Create the combined serializer class
    class LoginSerializer(
        response_serializer, auth_kit_settings.LOGIN_REQUEST_SERIALIZER  # type: ignore
    ):
        """User authentication with credentials response."""

        pass

    return LoginSerializer
