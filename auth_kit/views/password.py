from typing import Any

from django.http import HttpResponseBase
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from auth_kit.app_settings import auth_kit_settings
from auth_kit.utils import sensitive_post_parameters_m


class PasswordResetView(GenericAPIView[Any]):
    """
    Calls Django Auth PasswordResetForm save method.

    Accepts the following POST parameters: email
    Returns the success/fail message.
    """

    serializer_class = auth_kit_settings.PASSWORD_RESET_SERIALIZER
    permission_classes = (AllowAny,)
    authentication_classes = []
    throttle_scope = "auth_kit"

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
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
    Password reset e-mail link is confirmed, therefore
    this resets the user's password.

    Accepts the following POST parameters: token, uid,
        new_password1, new_password2
    Returns the success/fail message.
    """

    serializer_class = auth_kit_settings.PASSWORD_RESET_CONFIRM_SERIALIZER
    permission_classes = (AllowAny,)
    throttle_scope = "auth_kit"

    @sensitive_post_parameters_m
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponseBase:
        return super().dispatch(*args, **kwargs)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("Password has been reset with the new password.")},
        )


class PasswordChangeView(GenericAPIView[Any]):
    """
    Calls Django Auth SetPasswordForm save method.

    Returns the success/fail message.
    """

    serializer_class = auth_kit_settings.PASSWORD_CHANGE_SERIALIZER
    permission_classes = (IsAuthenticated,)
    throttle_scope = "auth_kit"

    @sensitive_post_parameters_m
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponseBase:
        return super().dispatch(*args, **kwargs)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("New password has been saved.")})
