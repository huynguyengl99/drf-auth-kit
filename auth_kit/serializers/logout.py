from typing import Any

from rest_framework import serializers
from rest_framework.serializers import Serializer

from auth_kit.app_settings import auth_kit_settings


class JWTLogoutSerializer(serializers.Serializer[dict[str, str]]):
    refresh = serializers.CharField(
        write_only=True, required=(not auth_kit_settings.USE_AUTH_COOKIE)
    )
    detail = serializers.CharField(read_only=True)


class AuthKitLogoutSerializer(serializers.Serializer[dict[str, str]]):
    detail = serializers.CharField(read_only=True)


LogoutSerializer: type[Serializer[Any]]

if auth_kit_settings.AUTH_TYPE == "jwt":
    LogoutSerializer = JWTLogoutSerializer
elif auth_kit_settings.AUTH_TYPE == "token":
    LogoutSerializer = AuthKitLogoutSerializer
else:
    LogoutSerializer = auth_kit_settings.CUSTOM_LOGOUT_SERIALIZER
