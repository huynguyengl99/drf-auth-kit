"""
Login serializer for Auth Kit.

This module provides the main login serializer that combines
request and response serialization functionality.
"""

from auth_kit.app_settings import auth_kit_settings


class LoginSerializer(
    auth_kit_settings.LOGIN_RESPONSE_SERIALIZER,  # type: ignore[misc,name-defined]
    auth_kit_settings.LOGIN_REQUEST_SERIALIZER,  # type: ignore[misc,name-defined]
):
    """User authentication with credentials response."""

    pass
