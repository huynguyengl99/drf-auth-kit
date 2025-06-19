from datetime import datetime

from rest_framework.response import Response

from .app_settings import auth_kit_settings


def set_auth_kit_cookie(
    response: Response,
    cookie_name: str,
    cookie_value: str,
    cookie_path: str,
    cookie_exp_time: datetime | None,
) -> None:
    response.set_cookie(
        cookie_name,
        cookie_value,
        expires=cookie_exp_time,
        secure=auth_kit_settings.AUTH_COOKIE_SECURE,
        httponly=auth_kit_settings.AUTH_COOKIE_HTTPONLY,
        samesite=auth_kit_settings.AUTH_COOKIE_SAMESITE,
        path=cookie_path,
        domain=auth_kit_settings.AUTH_COOKIE_DOMAIN,
    )


def unset_jwt_cookies(response: Response) -> None:
    cookie_samesite = auth_kit_settings.AUTH_COOKIE_SAMESITE
    cookie_domain = auth_kit_settings.AUTH_COOKIE_DOMAIN

    response.delete_cookie(
        auth_kit_settings.AUTH_JWT_COOKIE_NAME,
        samesite=cookie_samesite,
        domain=cookie_domain,
    )
    response.delete_cookie(
        auth_kit_settings.AUTH_JWT_REFRESH_COOKIE_NAME,
        path=auth_kit_settings.AUTH_JWT_REFRESH_COOKIE_PATH,
        samesite=cookie_samesite,
        domain=cookie_domain,
    )


def unset_token_cookie(response: Response) -> None:
    cookie_samesite = auth_kit_settings.AUTH_COOKIE_SAMESITE
    cookie_domain = auth_kit_settings.AUTH_COOKIE_DOMAIN

    response.delete_cookie(
        auth_kit_settings.AUTH_TOKEN_COOKIE_NAME,
        samesite=cookie_samesite,
        domain=cookie_domain,
    )
