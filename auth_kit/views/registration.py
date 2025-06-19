# pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false
from typing import Any, NoReturn
from urllib.parse import urlencode

from django.contrib.auth.models import AbstractUser
from django.http import HttpResponseBase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from allauth.account.app_settings import EmailVerificationMethod
from allauth.account.models import EmailAddress, get_emailconfirmation_model
from allauth.account.views import ConfirmEmailView
from allauth.utils import build_absolute_uri

from auth_kit.app_settings import auth_kit_settings
from auth_kit.serializers import (
    ResendEmailVerificationSerializer,
    VerifyEmailSerializer,
)
from auth_kit.utils import sensitive_post_parameters_m


def get_email_verification_url(request: Request, emailconfirmation: Any) -> str:
    query_params: dict[str, str] = {"key": str(emailconfirmation.key)}
    encoded_params = urlencode(query_params)

    if auth_kit_settings.REGISTER_EMAIL_CONFIRM_URL:
        url = f"{auth_kit_settings.REGISTER_EMAIL_CONFIRM_URL}?{encoded_params}"
    else:
        path = reverse("account_confirm_email")
        full_path = f"{path}?{encoded_params}"
        url = build_absolute_uri(request, full_path)

    return url


def send_verify_email(request: Request, user: AbstractUser) -> None:
    if allauth_account_settings.EMAIL_VERIFICATION == EmailVerificationMethod.NONE:
        return

    email_template = "account/email/email_confirmation_signup"

    email_address = EmailAddress.objects.get_for_user(  # pyright: ignore
        user, user.email  # pyright: ignore[reportUnknownMemberType]
    )
    model = get_emailconfirmation_model()
    emailconfirmation = model.create(email_address)  # pyright: ignore
    adapter = get_adapter()

    ctx: dict[str, Any] = {
        "user": user,
        "key": emailconfirmation.key,  # pyright: ignore[reportUnknownMemberType]
        "activate_url": auth_kit_settings.GET_EMAIL_VERIFICATION_URL_FUNC(
            request, emailconfirmation
        ),
    }
    adapter.send_mail(  # pyright: ignore[reportUnknownMemberType]
        email_template, emailconfirmation.email_address.email, ctx  # pyright: ignore
    )


class RegisterView(CreateAPIView[Any]):
    """
    Registers a new user.

    Accepts the following POST parameters: username, email, password1, password2.
    """

    serializer_class = auth_kit_settings.REGISTER_SERIALIZER
    authentication_classes = []
    throttle_scope = "auth_kit"

    @sensitive_post_parameters_m
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponseBase:
        return super().dispatch(*args, **kwargs)

    def get_response_data(self, user: AbstractUser) -> dict[str, Any]:
        if (
            allauth_account_settings.EMAIL_VERIFICATION
            == allauth_account_settings.EmailVerificationMethod.MANDATORY
        ):
            return {"detail": _("Verification e-mail sent.")}
        return {"detail": _("Successfully registered.")}

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        auth_kit_settings.SEND_VERIFY_EMAIL_FUNC(self.request, user)
        headers = self.get_success_headers(serializer.data)
        data = self.get_response_data(user)

        response = Response(
            data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

        return response


class VerifyEmailView(APIView, ConfirmEmailView):  # type: ignore[misc]
    """
    Verifies the email associated with the provided key.

    Accepts the following POST parameter: key.
    """

    permission_classes = (AllowAny,)
    authentication_classes = []

    def get_serializer(self, *args: Any, **kwargs: Any) -> VerifyEmailSerializer:
        return VerifyEmailSerializer(*args, **kwargs)

    def get(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise MethodNotAllowed("GET")

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs["key"] = serializer.validated_data["key"]
        confirmation = self.get_object()  # pyright: ignore[reportUnknownMemberType]
        confirmation.confirm(self.request)  # pyright: ignore[reportUnknownMemberType]
        return Response({"detail": _("ok")}, status=status.HTTP_200_OK)


class ResendEmailVerificationView(CreateAPIView[Any]):
    """
    Resends another email to an unverified email.

    Accepts the following POST parameter: email.
    """

    authentication_classes = []
    permission_classes = (AllowAny,)
    serializer_class = ResendEmailVerificationSerializer
    queryset = EmailAddress.objects.all()

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = self.get_queryset().filter(**serializer.validated_data).first()
        if email and not email.verified:
            auth_kit_settings.SEND_VERIFY_EMAIL_FUNC(self.request, email.user)

        return Response({"detail": _("ok")}, status=status.HTTP_200_OK)
