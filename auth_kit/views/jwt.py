from typing import Any

from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.views import TokenRefreshView

from auth_kit.app_settings import auth_kit_settings
from auth_kit.jwt_auth import set_auth_kit_cookie
from auth_kit.serializers import CookieTokenRefreshSerializer


class RefreshViewWithCookieSupport(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer  # type: ignore[assignment]

    def finalize_response(
        self, request: Request, response: Response, *args: Any, **kwargs: Any
    ) -> Response:
        if response.status_code == status.HTTP_200_OK and "access" in response.data:
            response.data["access_expiration"] = (
                timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME
            )
            set_auth_kit_cookie(
                response,
                auth_kit_settings.AUTH_JWT_COOKIE_NAME,
                response.data["access"],
                auth_kit_settings.AUTH_JWT_COOKIE_PATH,
                response.data["access_expiration"],
            )

        if response.status_code == status.HTTP_200_OK and "refresh" in response.data:
            response.data["refresh_expiration"] = (
                timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME
            )
            set_auth_kit_cookie(
                response,
                auth_kit_settings.AUTH_JWT_REFRESH_COOKIE_NAME,
                response.data["refresh"],
                auth_kit_settings.AUTH_JWT_REFRESH_COOKIE_PATH,
                response.data["refresh_expiration"],
            )

            if auth_kit_settings.AUTH_COOKIE_HTTPONLY:
                del response.data["refresh"]

        return super().finalize_response(request, response, *args, **kwargs)
