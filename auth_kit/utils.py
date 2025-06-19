from typing import Any, cast

from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


def jwt_encode(user: AbstractBaseUser) -> tuple[AccessToken, RefreshToken]:
    from auth_kit.app_settings import auth_kit_settings

    refresh: RefreshToken = auth_kit_settings.JWT_TOKEN_CLAIMS_SERIALIZER.get_token(user)  # type: ignore
    return refresh.access_token, refresh


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        "password",
        "old_password",
        "new_password1",
        "new_password2",
        "password1",
        "password2",
    ),
)


def cast_dict(arg: Any) -> dict[str, Any]:
    return cast(dict[str, Any], arg)
