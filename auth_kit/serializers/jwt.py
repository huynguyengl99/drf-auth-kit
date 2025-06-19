from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from auth_kit.app_settings import auth_kit_settings


class JWTSerializer(serializers.Serializer[dict[str, str]]):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    access_expiration = serializers.DateTimeField(read_only=True)
    refresh_expiration = serializers.DateTimeField(read_only=True)


class CookieTokenRefreshSerializer(TokenRefreshSerializer, JWTSerializer):
    refresh = serializers.CharField(
        required=False, help_text=_("WIll override cookie.")
    )

    def extract_refresh_token(self) -> str:
        request = self.context["request"]
        if "refresh" in request.data and request.data["refresh"] != "":
            return str(request.data["refresh"])
        cookie_name = auth_kit_settings.AUTH_JWT_REFRESH_COOKIE_NAME
        if cookie_name and cookie_name in request.COOKIES:
            return str(request.COOKIES.get(cookie_name))
        else:
            raise InvalidToken(str(_("No valid refresh token found.")))

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        attrs["refresh"] = self.extract_refresh_token()
        return super().validate(attrs)
