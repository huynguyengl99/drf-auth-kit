from typing import Any

from rest_framework.request import Request

from auth_kit.authentication import AuthKitCookieAuthentication
from knox.auth import TokenAuthentication  # pyright: ignore[reportMissingTypeStubs]

from custom_auth.constants import AUTH_KNOX_TOKEN_COOKIE_NAME


class KnoxTokenCookieAuthentication(TokenAuthentication, AuthKitCookieAuthentication):  # type: ignore[misc]
    keyword = "Bearer"

    def custom_authenticate(self, token: str) -> tuple[Any, Any] | None:
        return self.authenticate_credentials(token.encode("utf-8"))  # type: ignore[arg-type]

    def authenticate(self, request: Request) -> tuple[Any, Any] | None:
        return self._authenticate(request, AUTH_KNOX_TOKEN_COOKIE_NAME)
