from typing import Any

from rest_framework import serializers


class TokenSerializer(serializers.Serializer[dict[str, Any]]):
    """
    Serializer for Token model.
    """

    key = serializers.CharField(read_only=True)
