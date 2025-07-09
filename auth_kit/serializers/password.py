"""
Password management serializers for Auth Kit.

This module provides serializers for password reset, confirmation,
and change operations with integration to django-allauth.
"""

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
    url_str_to_user_pk as uid_decoder,
)

from auth_kit.app_settings import auth_kit_settings
from auth_kit.forms import AllAuthPasswordResetForm
from auth_kit.utils import UserModel, convert_form_errors_to_drf


class PasswordResetSerializer(serializers.Serializer[dict[str, Any]]):
    """Password reset request with email verification."""

    email = serializers.EmailField(write_only=True)
    detail = serializers.CharField(read_only=True)

    reset_form = None

    def get_email_options(self) -> dict[str, Any]:
        """
        Get email options for password reset.

        Override this method to change default email options.

        Returns:
            Dictionary of email options
        """
        return {}

    def validate_email(self, value: str) -> str:
        """
        Validate email address using password reset form.

        Args:
            value: Email address to validate

        Returns:
            Validated email address

        Raises:
            ValidationError: If email validation fails
        """
        # Create PasswordResetForm with the serializer
        self.reset_form = AllAuthPasswordResetForm(data=self.initial_data)
        assert self.reset_form.is_valid()

        return value

    def save(self, **kwargs: Any) -> dict[str, Any]:
        """
        Save password reset request and send email.

        Args:
            **kwargs: Additional keyword arguments

        Returns:
            Dictionary containing the email address
        """
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
    """Password reset confirmation with new password."""

    new_password1 = serializers.CharField(max_length=128, write_only=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True)
    uid = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    detail = serializers.CharField(read_only=True)

    set_password_form_class = SetPasswordForm

    user = None
    set_password_form = None

    def custom_validation(self, attrs: dict[str, Any]) -> None:
        """
        Perform custom validation on password reset data.

        Override this method to add custom validation logic.

        Args:
            attrs: Attributes dictionary to validate
        """
        pass

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate password reset confirmation data.

        Args:
            attrs: Input attributes dictionary

        Returns:
            Validated attributes

        Raises:
            ValidationError: If UID or token validation fails
        """
        # Decode the uidb64 (allauth use base36) to uid to get User object
        try:
            uid: str = force_str(
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
            raise serializers.ValidationError(
                convert_form_errors_to_drf(self.set_password_form)
            )

        return attrs

    def save(self, **kwargs: Any) -> AbstractBaseUser:  # type: ignore[override]
        """
        Save the new password for the user.

        Args:
            **kwargs: Additional keyword arguments

        Returns:
            The user instance with updated password
        """
        assert self.set_password_form
        return self.set_password_form.save()


class PasswordChangeSerializer(serializers.Serializer[dict[str, Any]]):
    """Password change for authenticated users."""

    old_password = serializers.CharField(max_length=128, write_only=True)

    new_password1 = serializers.CharField(max_length=128, write_only=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True)
    detail = serializers.CharField(read_only=True)

    set_password_form_class = SetPasswordForm

    set_password_form = None

    fields: dict[str, Any]  # type: ignore[assignment]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize password change serializer.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        super().__init__(*args, **kwargs)

        if not auth_kit_settings.OLD_PASSWORD_FIELD_ENABLED:
            self.fields.pop("old_password")

        self.request = self.context.get("request")
        self.user = getattr(self.request, "user", None)

    def validate_old_password(self, value: str) -> str:
        """
        Validate the old password if required.

        Args:
            value: Old password value to validate

        Returns:
            Validated old password

        Raises:
            ValidationError: If old password is incorrect
        """
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
        """
        Perform custom validation on password change data.

        Override this method to add custom validation logic.

        Args:
            attrs: Attributes dictionary to validate
        """
        pass

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate password change data.

        Args:
            attrs: Input attributes dictionary

        Returns:
            Validated attributes

        Raises:
            ValidationError: If password validation fails
        """
        assert self.user
        self.set_password_form = self.set_password_form_class(
            user=self.user,
            data=attrs,
        )

        self.custom_validation(attrs)
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(
                convert_form_errors_to_drf(self.set_password_form)
            )
        return attrs

    def save(self, **kwargs: Any) -> AbstractBaseUser:  # type: ignore[override]
        """
        Save the new password for the user.

        Args:
            **kwargs: Additional keyword arguments

        Returns:
            The user instance with updated password
        """
        assert self.set_password_form
        user: AbstractBaseUser = self.set_password_form.save()
        return user
