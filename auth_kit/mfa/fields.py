"""
Custom serializer fields for MFA functionality.

This module provides specialized field types for handling MFA method
selection and dispatch message serialization in API responses.
"""

from typing import Any

from rest_framework import serializers

from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema_field

from auth_kit.mfa.handlers.base import MFAHandlerRegistry
from auth_kit.mfa.utils import get_setup_data_schemas


@extend_schema_field(
    PolymorphicProxySerializer(
        component_name="MFAMethodSetupData",
        serializers=get_setup_data_schemas(),
        resource_type_field_name=None,
    )
)
class MFAMethodSetupDataField(serializers.DictField):
    """
    Field for MFA method dispatch messages.

    Handles polymorphic serialization of method-specific setup data
    such as QR codes for authenticator apps or confirmation messages
    for email-based methods.
    """

    pass


class MFAMethodField(serializers.ChoiceField):
    """
    Field for MFA method selection.

    Provides choices based on currently registered MFA handlers.
    Choices are dynamically generated from the handler registry.

    Args:
        **kwargs: Additional field arguments passed to ChoiceField
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize field with dynamic choices from handler registry.

        Args:
            **kwargs: Additional field arguments
        """
        choices = [(k, k) for k in MFAHandlerRegistry.list_handler_names()]
        super().__init__(choices, **kwargs)
