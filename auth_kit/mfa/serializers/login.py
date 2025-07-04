"""
Combined serializers for MFA login flow.

This module provides factory functions that create combined serializers
for the two-step MFA authentication process by merging request and
response serializers based on current settings.
"""

from typing import Any

from rest_framework.serializers import Serializer

from auth_kit.app_settings import auth_kit_settings
from auth_kit.mfa.mfa_settings import auth_kit_mfa_settings
from auth_kit.serializers.login_factors import get_login_response_serializer


def get_mfa_first_step_serializer() -> type[Serializer[dict[str, Any]]]:
    """
    Get combined serializer for first step MFA authentication.

    Combines login request serializer with MFA first step response
    serializer to handle credential validation and MFA initiation.

    Returns:
        Combined serializer class for first step authentication
    """

    class MFAFirstStepSerializer(
        auth_kit_mfa_settings.MFA_FIRST_STEP_RESPONSE_SERIALIZER,  # type: ignore
        auth_kit_settings.LOGIN_REQUEST_SERIALIZER,  # type: ignore
    ):
        """First step MFA authentication serializer."""

        pass

    return MFAFirstStepSerializer


def get_mfa_second_step_serializer() -> type[Serializer[dict[str, Any]]]:
    """
    Get combined serializer for second step MFA authentication.

    Combines MFA verification request serializer with login response
    serializer to handle code verification and token generation.

    Returns:
        Combined serializer class for second step authentication
    """
    response_serializer = get_login_response_serializer()

    class MFASecondStepSerializer(
        response_serializer,  # type: ignore
        auth_kit_mfa_settings.MFA_SECOND_STEP_REQUEST_SERIALIZER,  # type: ignore
    ):
        """Second step MFA authentication serializer."""

        pass

    return MFASecondStepSerializer
