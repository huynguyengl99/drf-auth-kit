"""
Serializers for the myapp module.

This module defines serializers used by the myapp API views.
Serializers handle the conversion between complex data types and
Python native datatypes that can be easily rendered into JSON, XML, etc.
"""

from typing import Any

from rest_framework import serializers


class MyModelSerializer(serializers.Serializer[dict[Any, Any]]):
    """
    Serializer for handling MyModel data.

    This serializer validates and processes payload data for the MyModel API.
    It uses generic typing to define the return type as a dictionary.

    Attributes:
        payload (CharField): A text field that stores the payload data.
    """

    payload = serializers.CharField()
