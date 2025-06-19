"""
Custom serializer fields for Auth Kit.

This module provides specialized field types for handling
URL-encoded and other specific data formats in API serializers.
"""

from urllib.parse import unquote_plus

from rest_framework import serializers


class UnquoteStringField(serializers.CharField):
    """
    CharField that automatically URL-decodes input values.

    Useful for handling URL-encoded strings in API requests,
    particularly for email verification tokens and similar data.
    """

    def to_internal_value(self, data: str) -> str:
        """
        Convert URL-encoded string to internal representation.

        Args:
            data: URL-encoded string input

        Returns:
            URL-decoded string
        """
        return unquote_plus(data)
