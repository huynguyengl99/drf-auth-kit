from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework.authentication import BaseAuthentication, TokenAuthentication
from rest_framework.request import Request

from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from rest_framework_simplejwt.authentication import JWTAuthentication

from auth_kit.app_settings import auth_kit_settings


class AuthKitCookieAuthentication(JWTAuthentication):
    """
    An authentication plugin that hopefully authenticates requests through a JSON web
    token provided in a request cookie (and through the header as normal, with a
    preference to the header).
    """

    def _authenticate(
        self, request: Request, cookie_name: str | None
    ) -> tuple[Any, Any] | None:
        header = self.get_header(request)
        if header is None:  # pyright: ignore[reportUnnecessaryComparison]
            if cookie_name:
                raw_token = request.COOKIES.get(cookie_name)
                raw_token = raw_token.encode("utf-8") if raw_token else None
            else:
                return None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        token = raw_token.decode()

        if auth_kit_settings.AUTH_TYPE == "jwt":
            validated_token = self.get_validated_token(raw_token)
            user: AbstractBaseUser = self.get_user(validated_token)
            return user, validated_token
        elif auth_kit_settings.AUTH_TYPE == "token":
            return self.authenticate_credentials(token)
        else:
            return self.custom_authenticate(token)

    def authenticate_credentials(self, key: str) -> tuple[Any, Any] | None:
        pass

    def custom_authenticate(self, token: str) -> tuple[Any, Any] | None:
        pass


class TokenCookieAuthentication(TokenAuthentication, AuthKitCookieAuthentication):
    keyword = "Bearer"

    def authenticate(self, request: Request) -> tuple[Any, Any] | None:
        return self._authenticate(request, auth_kit_settings.AUTH_TOKEN_COOKIE_NAME)


class TokenCookieAuthenticationScheme(SimpleJWTScheme):  # type: ignore[no-untyped-call]
    target_class = "auth_kit.authentication.TokenCookieAuthentication"
    optional = True
    name = [  # type: ignore[assignment]
        "TokenAuthentication",
        "TokenCookieAuthentication",
    ]  # name used in the schema

    def get_security_definition(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, auto_schema: Any
    ) -> list[dict[str, Any]]:
        return [
            super().get_security_definition(auto_schema),  # type: ignore[no-untyped-call]
            {
                "type": "apiKey",
                "in": "cookie",
                "name": auth_kit_settings.AUTH_JWT_COOKIE_NAME,
            },
        ]


class JWTCookieAuthentication(AuthKitCookieAuthentication):
    def authenticate(self, request: Request) -> tuple[Any, Any] | None:
        return self._authenticate(request, auth_kit_settings.AUTH_JWT_COOKIE_NAME)


class JWTCookieAuthenticationScheme(SimpleJWTScheme):  # type: ignore[no-untyped-call]
    target_class = "auth_kit.authentication.JWTCookieAuthentication"
    optional = True
    name = ["JWTAuthentication", "JWTCookieAuthentication"]  # type: ignore[assignment]

    def get_security_definition(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, auto_schema: Any
    ) -> list[dict[str, Any]]:
        return [
            super().get_security_definition(auto_schema),  # type: ignore[no-untyped-call]
            {
                "type": "apiKey",
                "in": "cookie",
                "name": auth_kit_settings.AUTH_JWT_COOKIE_NAME,
            },
        ]


AuthKitAuthentication: type[BaseAuthentication]
if auth_kit_settings.AUTH_TYPE == "jwt":
    AuthKitAuthentication = JWTCookieAuthentication
elif auth_kit_settings.AUTH_TYPE == "token":
    AuthKitAuthentication = TokenCookieAuthentication
else:
    AuthKitAuthentication = auth_kit_settings.CUSTOM_AUTHENTICATION
