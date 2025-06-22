"""
Password management views for Auth Kit.

This module provides views for password reset, confirmation,
and change operations.
"""

from typing import Any

from django.http import HttpResponseBase
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema,
)

from auth_kit.api_descriptions import (
    PASSWORD_CHANGE_DESCRIPTION,
    PASSWORD_RESET_CONFIRM_DESCRIPTION,
    PASSWORD_RESET_DESCRIPTION,
)
from auth_kit.app_settings import auth_kit_settings
from auth_kit.utils import sensitive_post_parameters_m


class PasswordResetView(GenericAPIView[Any]):
    """
    Password reset request view.

    Accepts email address and sends password reset email
    using django-allauth forms.
    """

    serializer_class = auth_kit_settings.PASSWORD_RESET_SERIALIZER
    permission_classes = (AllowAny,)
    authentication_classes = []
    throttle_scope = "auth_kit"

    @extend_schema(description=PASSWORD_RESET_DESCRIPTION)
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle POST request for password reset.

        Args:
            request: The HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            HTTP response with success message
        """
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        # Return the success message with OK HTTP status
        return Response(
            {"detail": _("Password reset e-mail has been sent.")},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(GenericAPIView[Any]):
    """
    Password reset confirmation view.

    Validates reset token and sets new password for the user.
    """

    serializer_class = auth_kit_settings.PASSWORD_RESET_CONFIRM_SERIALIZER
    permission_classes = (AllowAny,)
    throttle_scope = "auth_kit"

    @sensitive_post_parameters_m
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponseBase:
        """
        Dispatch the request with sensitive parameter protection.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            HTTP response
        """
        return super().dispatch(*args, **kwargs)

    @extend_schema(description=PASSWORD_RESET_CONFIRM_DESCRIPTION)
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle POST request for password reset confirmation.

        Args:
            request: The HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            HTTP response with success message
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("Password has been reset with the new password.")},
        )


class PasswordChangeView(GenericAPIView[Any]):
    """
    Password change view for authenticated users.

    Allows authenticated users to change their password.
    """

    serializer_class = auth_kit_settings.PASSWORD_CHANGE_SERIALIZER
    permission_classes = (IsAuthenticated,)
    throttle_scope = "auth_kit"

    @sensitive_post_parameters_m
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponseBase:
        """
        Dispatch the request with sensitive parameter protection.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            HTTP response
        """
        return super().dispatch(*args, **kwargs)

    @extend_schema(description=PASSWORD_CHANGE_DESCRIPTION)
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle POST request for password change.

        Args:
            request: The HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            HTTP response with success message
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("New password has been saved.")})
