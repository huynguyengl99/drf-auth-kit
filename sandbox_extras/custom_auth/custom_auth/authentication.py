from typing import Any

from rest_framework.request import Request

from auth_kit.authentication import AuthKitCookieAuthentication
from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from knox.auth import TokenAuthentication  # pyright: ignore[reportMissingTypeStubs]

from custom_auth.constants import AUTH_KNOX_TOKEN_COOKIE_NAME


class KnoxTokenCookieAuthentication(TokenAuthentication, AuthKitCookieAuthentication):  # type: ignore[misc]
    keyword = "Bearer"

    def custom_authenticate(self, token: str) -> tuple[Any, Any] | None:
        return self.authenticate_credentials(token.encode("utf-8"))  # type: ignore[arg-type]

    def authenticate(self, request: Request) -> tuple[Any, Any] | None:
        return self.authenticate_with_cookie(request, AUTH_KNOX_TOKEN_COOKIE_NAME)


class KnoxTokenCookieAuthenticationScheme(SimpleJWTScheme):  # type: ignore[no-untyped-call]
    """OpenAPI schema for knox token cookie authentication."""

    target_class = "custom_auth.authentication.KnoxTokenCookieAuthentication"
    optional = True
    name = [  # type: ignore[assignment]
        "KnoxTokenAuthentication",
        "KnoxTokenCookieAuthentication",
    ]  # name used in the schema

    def get_security_definition(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, auto_schema: Any
    ) -> list[dict[str, Any]]:
        """
        Get security definition for OpenAPI schema.

        Args:
            auto_schema: The auto schema generator instance

        Returns:
            List of security definitions for the schema
        """
        return [
            build_bearer_security_scheme_object(
                header_name="HTTP_AUTHORIZATION",
                token_prefix=KnoxTokenCookieAuthentication.keyword,
                bearer_format="DRF Token",
            ),
            {
                "type": "apiKey",
                "in": "cookie",
                "name": AUTH_KNOX_TOKEN_COOKIE_NAME,
            },
        ]
