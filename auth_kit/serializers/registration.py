# pyright: reportUnknownMemberType=false
from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from allauth.account.adapter import (  # pyright: ignore[reportMissingTypeStubs]
    get_adapter,  # pyright: ignore[reportUnknownVariableType]
)
from allauth.account.models import (  # pyright: ignore[reportMissingTypeStubs]
    EmailAddress,
)
from allauth.account.utils import (  # pyright: ignore[reportMissingTypeStubs]
    setup_user_email,  # pyright: ignore[reportUnknownVariableType]
)

from auth_kit.serializer_fields import UnquoteStringField
from auth_kit.serializers.login_factors import UserNameField


class RegisterSerializer(serializers.Serializer[dict[str, Any]]):
    if UserNameField == "username":
        username = serializers.CharField(write_only=True)

    email = serializers.EmailField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    detail = serializers.CharField(read_only=True)

    def validate_username(self, username: str) -> str:
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email: str) -> str:
        email = get_adapter().clean_email(email)
        if EmailAddress.objects.filter(email=email).exists():
            raise ValidationError(
                _("A user is already registered with this e-mail address.")
            )
        return email

    def validate_password1(self, password: str) -> str:
        return str(get_adapter().clean_password(password))

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )
        return attrs

    def custom_signup(self, request: Request, user: AbstractBaseUser) -> None:
        pass

    def get_cleaned_data(self) -> dict[str, Any]:
        return {
            "username": self.validated_data.get("username", ""),
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
        }

    def save(self, **kwargs: Any) -> AbstractBaseUser:  # type: ignore[override]
        request = self.context["request"]
        adapter = get_adapter()
        user: AbstractBaseUser = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()

        user = adapter.save_user(request, user, self, commit=False)
        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data["password1"], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                ) from exc
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class VerifyEmailSerializer(serializers.Serializer[dict[str, Any]]):
    key = UnquoteStringField(required=True, write_only=True)
    detail = serializers.CharField(read_only=True)


class ResendEmailVerificationSerializer(serializers.Serializer[dict[str, Any]]):
    email = serializers.EmailField(required=True, write_only=True)
    detail = serializers.CharField(read_only=True)
