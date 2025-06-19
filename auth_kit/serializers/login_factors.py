from typing import Any, cast

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.serializers import Serializer

from allauth.account import (  # pyright: ignore[reportMissingTypeStubs]
    app_settings as allauth_account_settings,
)
from allauth.account.models import (  # pyright: ignore[reportMissingTypeStubs]
    EmailAddress,
)
from drf_spectacular.utils import (
    extend_schema_field,  # pyright: ignore[reportUnknownVariableType]
)
from rest_framework_simplejwt.settings import api_settings as jwt_settings

from auth_kit.app_settings import auth_kit_settings
from auth_kit.serializers import JWTSerializer
from auth_kit.serializers.token import TokenSerializer
from auth_kit.utils import cast_dict, jwt_encode

UserModel: type[User] = get_user_model()  # type: ignore[assignment, unused-ignore]
UserNameField: str = UserModel.USERNAME_FIELD


class LoginRequestSerializer(serializers.Serializer[dict[str, Any]]):
    if UserNameField == "username":
        username = serializers.CharField(write_only=True)
    elif UserNameField == "email":
        email = serializers.EmailField(write_only=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    def authenticate(self, **kwargs: Any) -> AbstractBaseUser | None:
        return authenticate(self.context["request"], **kwargs)

    def get_auth_user(
        self, username: str | None, email: str | None, password: str | None
    ) -> AbstractBaseUser | None:
        # Authentication through email
        if UserModel.USERNAME_FIELD == "email":
            return self.authenticate(email=email, password=password)
        elif UserModel.USERNAME_FIELD == "username":
            return self.authenticate(username=username, password=password)
        else:
            return None

    @staticmethod
    def validate_auth_user_status(user: AbstractBaseUser | None) -> None:
        if user and not user.is_active:
            msg = _("User account is disabled.")
            raise exceptions.ValidationError(msg)

    def validate_email_verification_status(self, user: AbstractBaseUser) -> None:
        user_email_queryset = cast(
            QuerySet[EmailAddress],
            user.emailaddress_set,  # type: ignore
        )
        user_email: str = user.email  # type: ignore
        if (
            allauth_account_settings.EMAIL_VERIFICATION
            == allauth_account_settings.EmailVerificationMethod.MANDATORY
            and not user_email_queryset.filter(
                email=user_email,
                verified=True,
            ).exists()
        ):
            raise serializers.ValidationError(_("E-mail is not verified."))

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        super().validate(attrs)
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")
        user = self.get_auth_user(username, email, password)

        if not user:
            msg = _("Unable to log in with provided credentials.")
            raise exceptions.ValidationError(msg)

        # Did we get back an active user?
        self.validate_auth_user_status(user)

        # If required, is the email verified?
        self.validate_email_verification_status(user)

        self.context["user"] = user
        return attrs


class BaseLoginResponseSerializer(serializers.Serializer[dict[str, Any]]):
    user = serializers.SerializerMethodField()

    @extend_schema_field(auth_kit_settings.USER_DETAILS_SERIALIZER)
    def get_user(self, obj: dict[str, Any]) -> dict[str, Any]:
        user_detail_serializer = auth_kit_settings.USER_DETAILS_SERIALIZER(
            obj["user"], context=self.context
        )
        return cast_dict(
            user_detail_serializer.data  # pyright: ignore[reportUnknownMemberType]
        )


class JWTResponseSerializer(JWTSerializer, BaseLoginResponseSerializer):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        super().validate(attrs)
        user = self.context["user"]
        access_token_expiration = timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME
        refresh_token_expiration = timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME

        access_token, refresh_token = jwt_encode(user)

        data = {
            "user": user,
            "access": access_token,
            "refresh": refresh_token,
            "access_expiration": access_token_expiration,
            "refresh_expiration": refresh_token_expiration,
        }

        return data


class TokenResponseSerializer(TokenSerializer, BaseLoginResponseSerializer):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        super().validate(attrs)
        user = self.context["user"]
        token, _ = auth_kit_settings.AUTH_TOKEN_MODEL.objects.get_or_create(user=user)

        return {
            "user": user,
            "key": token.key,  # pyright: ignore[reportUnknownMemberType]
        }


LoginResponseSerializer: type[Serializer[Any]]

if auth_kit_settings.AUTH_TYPE == "jwt":
    LoginResponseSerializer = JWTResponseSerializer
elif auth_kit_settings.AUTH_TYPE == "token":
    LoginResponseSerializer = TokenResponseSerializer
else:
    LoginResponseSerializer = auth_kit_settings.CUSTOM_LOGIN_RESPONSE_SERIALIZER
