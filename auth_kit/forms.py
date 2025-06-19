# pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false
from typing import Any
from urllib.parse import urlencode

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
from django.urls import reverse

from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import ResetPasswordForm as DefaultPasswordResetForm
from allauth.account.forms import default_token_generator
from allauth.account.utils import (
    user_pk_to_url_str,
    user_username,
)
from allauth.utils import build_absolute_uri

from .app_settings import auth_kit_settings


def password_reset_url_generator(
    request: HttpRequest, user: AbstractUser, temp_key: str
) -> str:
    uid = user_pk_to_url_str(user)

    query_params: dict[str, str] = {"uid": uid, "token": temp_key}
    encoded_params = urlencode(query_params)

    if auth_kit_settings.PASSWORD_RESET_CONFIRM_URL:
        url = f"{auth_kit_settings.PASSWORD_RESET_CONFIRM_URL}?{encoded_params}"
    else:
        path = reverse("rest_password_reset_confirm")
        full_path = f"{path}?{encoded_params}"
        url = build_absolute_uri(request, full_path)

    return url


class AllAuthPasswordResetForm(DefaultPasswordResetForm):  # type: ignore[misc]
    def save(self, request: HttpRequest, **kwargs: Any) -> str:
        email: str = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator", default_token_generator)

        users: list[AbstractBaseUser] = (  # pyright: ignore[reportUnknownMemberType]
            self.users
        )

        for user in users:
            temp_key: str = token_generator.make_token(user)

            # send the password reset email
            url_generator = kwargs.get(
                "url_generator", auth_kit_settings.PASSWORD_RESET_URL_GENERATOR
            )
            url: str = url_generator(request, user, temp_key)
            uid: str = user_pk_to_url_str(user)

            context: dict[str, Any] = {
                "user": user,
                "password_reset_url": url,
                "request": request,
                "token": temp_key,
                "uid": uid,
            }
            if (
                allauth_account_settings.AuthenticationMethod.USERNAME
                in allauth_account_settings.LOGIN_METHODS
            ):
                context["username"] = user_username(user)
            get_adapter(request).send_mail(  # pyright: ignore[reportUnknownMemberType]
                "account/email/password_reset_key", email, context
            )
        return str(self.cleaned_data["email"])
