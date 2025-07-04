"""
Utility functions for MFA functionality.

This module provides helper functions for schema generation and
handler management in the MFA system.
"""

from typing import Any

from rest_framework.serializers import Serializer

from auth_kit.mfa.handlers.base import MFAHandlerRegistry


def get_setup_data_schemas() -> list[type[Serializer[Any]]]:
    """
    Get serializer classes for all handler dispatch messages.

    Used for generating polymorphic OpenAPI schemas that show
    different response formats for various MFA method types.

    Returns:
        List of serializer classes for method setup responses
    """
    handlers = MFAHandlerRegistry.get_handlers()
    return [
        handler.get_initialize_method_serializer_class()
        for handler in handlers.values()
    ]
