from typing import Any, cast

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.forms import SetPasswordForm
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from allauth.account.forms import (  # pyright: ignore[reportMissingTypeStubs]
    default_token_generator,
)
from allauth.account.utils import (  # pyright: ignore[reportMissingTypeStubs]
    url_str_to_user_pk as uid_decoder,  # pyright: ignore[reportUnknownVariableType]
)

from auth_kit.app_settings import auth_kit_settings
from auth_kit.forms import AllAuthPasswordResetForm
from auth_kit.serializers.login_factors import UserModel


class PasswordResetSerializer(serializers.Serializer[dict[str, Any]]):
    """
    Serializer for requesting a password reset e-mail.
    """

    email = serializers.EmailField(write_only=True)
    detail = serializers.CharField(read_only=True)

    reset_form = None

    def get_email_options(self) -> dict[str, Any]:
        """Override this method to change default e-mail options"""
        return {}

    def validate_email(self, value: str) -> str:
        # Create PasswordResetForm with the serializer
        self.reset_form = AllAuthPasswordResetForm(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(str(self.reset_form.errors))

        return value

    def save(self, **kwargs: Any) -> dict[str, Any]:
        request = cast(Request, self.context.get("request"))
        # Set some values to trigger the send_email method.
        opts = {
            "token_generator": default_token_generator,
        }

        opts.update(self.get_email_options())
        assert self.reset_form
        email = self.reset_form.save(request, **opts)
        return {
            "email": email,
        }


class PasswordResetConfirmSerializer(serializers.Serializer[dict[str, Any]]):
    """
    Serializer for confirming a password reset attempt.
    """

    new_password1 = serializers.CharField(max_length=128, write_only=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True)
    uid = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    detail = serializers.CharField(read_only=True)

    set_password_form_class = SetPasswordForm

    user = None
    set_password_form = None

    def custom_validation(self, attrs: dict[str, Any]) -> None:
        pass

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # Decode the uidb64 (allauth use base36) to uid to get User object
        try:
            uid: str = force_str(  # pyright: ignore[reportUnknownVariableType]
                uid_decoder(attrs["uid"])  # pyright: ignore[reportUnknownArgumentType]
            )
            self.user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist) as err:
            raise ValidationError({"uid": [_("Invalid value")]}) from err

        if not default_token_generator.check_token(self.user, attrs["token"]):
            raise ValidationError({"token": [_("Invalid value")]})

        self.custom_validation(attrs)
        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user,
            data=attrs,
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(str(self.set_password_form.errors))

        return attrs

    def save(self, **kwargs: Any) -> AbstractBaseUser:  # type: ignore[override]
        assert self.set_password_form
        return self.set_password_form.save()


class PasswordChangeSerializer(serializers.Serializer[dict[str, Any]]):
    if auth_kit_settings.OLD_PASSWORD_FIELD_ENABLED:
        old_password = serializers.CharField(max_length=128, write_only=True)

    new_password1 = serializers.CharField(max_length=128, write_only=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True)
    detail = serializers.CharField(read_only=True)

    set_password_form_class = SetPasswordForm

    set_password_form = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.request = self.context.get("request")
        self.user = getattr(self.request, "user", None)

    def validate_old_password(self, value: str) -> str:
        assert self.user
        invalid_password_conditions = (
            auth_kit_settings.OLD_PASSWORD_FIELD_ENABLED,
            self.user,
            not self.user.check_password(value),
        )

        if all(invalid_password_conditions):
            err_msg = _(
                "Your old password was entered incorrectly. Please enter it again."
            )
            raise serializers.ValidationError(err_msg)
        return value

    def custom_validation(self, attrs: dict[str, Any]) -> None:
        pass

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        assert self.user
        self.set_password_form = (
            self.set_password_form_class(  # pyright: ignore[reportUnknownMemberType]
                user=self.user,
                data=attrs,
            )
        )

        self.custom_validation(attrs)
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(str(self.set_password_form.errors))
        return attrs

    def save(self, **kwargs: Any) -> AbstractBaseUser:  # type: ignore[override]
        assert self.set_password_form
        user: AbstractBaseUser = self.set_password_form.save()
        return user
