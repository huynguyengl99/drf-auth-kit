"""
Custom exceptions for MFA functionality.

This module provides specialized exception classes for handling
MFA-related validation errors and method management issues.
"""

from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import ValidationError


class MFAMethodDoesNotExistError(ValidationError):
    """
    Exception raised when requested MFA method does not exist.

    Used when attempting to access, validate, or manage an MFA method
    that is not found in the database for the specified user.

    Attributes:
        detail: Human-readable error message
        code: Machine-readable error code
    """

    def __init__(self) -> None:
        """Initialize exception with default error message and code."""
        super().__init__(
            detail=_("Requested MFA method does not exist."),
            code="mfa_method_does_not_exist",
        )
