# pyright: reportMissingTypeStubs=false
from datetime import datetime, timedelta
from typing import Any

from django.contrib.auth import user_logged_in
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.fields import DateTimeField

from auth_kit.serializers.login_factors import BaseLoginResponseSerializer
from knox.models import AuthToken, get_token_model
from knox.settings import knox_settings


class KnoxTokenSerializer(serializers.Serializer[dict[str, Any]]):
    """
    Serializer for Token model.
    """

    token = serializers.CharField(read_only=True)
    expiry = serializers.DateTimeField(read_only=True)


class KnoxTokenResponseSerializer(KnoxTokenSerializer, BaseLoginResponseSerializer):
    def get_token_ttl(self) -> timedelta:
        return timedelta(knox_settings.TOKEN_TTL)

    def get_token_prefix(self) -> str:
        return str(knox_settings.TOKEN_PREFIX)

    def get_token_limit_per_user(self) -> int | None:
        if knox_settings.TOKEN_LIMIT_PER_USER is None:
            return None
        return int(knox_settings.TOKEN_LIMIT_PER_USER)

    def get_expiry_datetime_format(self) -> str:
        return str(knox_settings.EXPIRY_DATETIME_FORMAT)

    def format_expiry_datetime(self, expiry: datetime) -> str:
        datetime_format = self.get_expiry_datetime_format()
        return DateTimeField(format=datetime_format).to_representation(expiry)

    def create_token(self, user: AbstractBaseUser) -> tuple[AuthToken, str]:
        token_prefix = self.get_token_prefix()
        return get_token_model().objects.create(  # type: ignore[no-any-return]
            user=user, expiry=self.get_token_ttl(), prefix=token_prefix
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        super().validate(attrs)
        user = self.context["user"]
        request = self.context["request"]
        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = timezone.now()
            token = user.auth_token_set.filter(expiry__gt=now)
            if token.count() >= token_limit_per_user:
                raise PermissionDenied(
                    "Maximum amount of tokens allowed per user exceeded."
                )
        instance, token = self.create_token(user)
        user_logged_in.send(  # pyright: ignore[reportUnknownMemberType]
            sender=request.user.__class__, request=request, user=user
        )

        return {
            "user": user,
            "token": token,
            "expiry": self.format_expiry_datetime(instance.expiry),  # pyright: ignore
        }
