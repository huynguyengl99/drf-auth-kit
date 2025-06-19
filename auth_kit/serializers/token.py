"""
Token serializers for Auth Kit.

This module provides serializers for DRF token authentication.
"""

from typing import Any

from rest_framework import serializers


class TokenSerializer(serializers.Serializer[dict[str, Any]]):
    """DRF authentication token."""

    key = serializers.CharField(read_only=True)
