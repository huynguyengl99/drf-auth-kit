"""
Logout serializers for Auth Kit.

This module provides serializers for handling logout requests
with support for different authentication types.
"""

from functools import lru_cache
from typing import Any

from rest_framework import serializers
from rest_framework.serializers import Serializer

from auth_kit.app_settings import auth_kit_settings


class JWTLogoutSerializer(serializers.Serializer[dict[str, str]]):
    """JWT logout with refresh token blacklisting."""

    refresh = serializers.CharField(
        write_only=True, required=(not auth_kit_settings.USE_AUTH_COOKIE)
    )
    detail = serializers.CharField(read_only=True)


class AuthKitLogoutSerializer(serializers.Serializer[dict[str, str]]):
    """Logout confirmation for token-based authentication."""

    detail = serializers.CharField(read_only=True)


@lru_cache
def get_logout_serializer() -> type[Serializer[dict[str, Any]]]:
    """
    Get the appropriate logout serializer based on current settings.

    Returns:
        The appropriate logout serializer class
    """
    if auth_kit_settings.LOGOUT_SERIALIZER != AuthKitLogoutSerializer:
        return auth_kit_settings.LOGOUT_SERIALIZER

    if auth_kit_settings.AUTH_TYPE == "jwt":
        return JWTLogoutSerializer
    return AuthKitLogoutSerializer
