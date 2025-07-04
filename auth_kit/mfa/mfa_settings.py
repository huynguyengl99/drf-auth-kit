"""
Configuration settings for Auth Kit MFA package.

This module provides a centralized configuration system for MFA functionality,
allowing dynamic loading of handlers, serializers, views, and authentication
classes based on user settings.
"""

# pyright: reportAssignmentType=false
# mypy: disable-error-code=assignment

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from django.conf import settings
from django.core.signals import setting_changed
from rest_framework.serializers import Serializer
from rest_framework.settings import APISettings

if TYPE_CHECKING:
    from auth_kit.mfa.handlers.base import MFABaseHandler
    from auth_kit.mfa.models import MFAMethod
    from auth_kit.mfa.serializers.login_factors import (
        MFAChangeMethodSerializer,
        MFAFirstStepResponseSerializer,
        MFAResendSerializer,
        MFASecondStepRequestSerializer,
    )
    from auth_kit.mfa.serializers.mfa import (
        MFAMethodConfigSerializer,
        MFAMethodConfirmSerializer,
        MFAMethodCreateSerializer,
        MFAMethodDeactivateSerializer,
        MFAMethodDeleteSerializer,
        MFAMethodPrimaryUpdateSerializer,
        MFAMethodSendCodeSerializer,
    )
    from auth_kit.mfa.views import (
        LoginChangeMethodView,
        LoginFirstStepView,
        LoginMFAResendView,
        LoginSecondStepView,
        MFAMethodViewSet,
    )


class Importable:
    """Base class for marking settings as requiring import resolution."""

    pass


class StringImport(Importable, str):
    """String import marker for individual import strings."""

    pass


class ListImport(Importable, list[str]):
    """List import marker for collections of import strings."""

    pass


class ImportStr:
    """
    Factory for creating importable setting values.

    Automatically detects whether input is a single string or list/tuple
    and returns appropriate importable type.
    """

    def __new__(cls, val: str | list[str] | tuple[str], *args: Any, **kwargs: Any) -> StringImport | ListImport:  # type: ignore[misc]
        """
        Create appropriate importable type based on input.

        Args:
            val: Value to make importable

        Returns:
            Importable wrapper for the value
        """
        if isinstance(val, list | tuple):
            return ListImport(val)
        return StringImport(val)


class MFASetting:
    """
    Default MFA settings configuration for Auth Kit.

    Provides all configurable options for MFA functionality including
    handler configuration, security settings, view/serializer classes,
    and behavioral constraints.
    """

    # MFA Model Configuration
    MFA_MODEL: type["MFAMethod"] = ImportStr("auth_kit.mfa.models.MFAMethod")

    # Handler Configuration
    MFA_HANDLERS: list[type["MFABaseHandler"]] = ImportStr(
        [
            "auth_kit.mfa.handlers.app.MFAAppHandler",
            "auth_kit.mfa.handlers.email.MFAEmailHandler",
        ]
    )

    # Backup Code Settings
    NUM_OF_BACKUP_CODES: int = 5
    BACKUP_CODE_LENGTH: int = 12
    BACKUP_CODE_ALLOWED_CHARS: str = (
        "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford Base32
    )
    BACKUP_CODE_SECURE_HASH: bool = True

    # TOTP Configuration
    MFA_TOTP_DEFAULT_VALID_WINDOW: int = 0  # seconds
    MFA_TOTP_DEFAULT_INTERVAL: int = 30  # seconds

    # Application Settings
    MFA_APPLICATION_NAME: str = "MyApplication"

    # Token Expiry Configuration
    MFA_EPHEMERAL_TOKEN_EXPIRY: int = 60 * 15  # 15 minutes in seconds

    # MFA Update Constraints
    MFA_UPDATE_PRIMARY_METHOD_REQUIRED_PRIMARY_CODE: bool = False
    MFA_PREVENT_DELETE_ACTIVE_METHOD: bool = False
    MFA_PREVENT_DELETE_PRIMARY_METHOD: bool = False
    MFA_DELETE_ACTIVE_METHOD_REQUIRE_CODE: bool = False

    # MFA Views Configuration
    LOGIN_FIRST_STEP_VIEW: type["LoginFirstStepView"] = ImportStr(
        "auth_kit.mfa.views.LoginFirstStepView"
    )
    LOGIN_SECOND_STEP_VIEW: type["LoginSecondStepView"] = ImportStr(
        "auth_kit.mfa.views.LoginSecondStepView"
    )
    LOGIN_CHANGE_METHOD_VIEW: type["LoginChangeMethodView"] = ImportStr(
        "auth_kit.mfa.views.LoginChangeMethodView"
    )
    LOGIN_MFA_RESEND_VIEW: type["LoginMFAResendView"] = ImportStr(
        "auth_kit.mfa.views.LoginMFAResendView"
    )
    LOGIN_MFA_METHOD_VIEW_SET: type["MFAMethodViewSet"] = ImportStr(
        "auth_kit.mfa.views.MFAMethodViewSet"
    )

    # MFA Response Serializers
    MFA_FIRST_STEP_RESPONSE_SERIALIZER: type["MFAFirstStepResponseSerializer"] = (
        ImportStr(
            "auth_kit.mfa.serializers.login_factors.MFAFirstStepResponseSerializer"
        )
    )
    MFA_SECOND_STEP_REQUEST_SERIALIZER: type["MFASecondStepRequestSerializer"] = (
        ImportStr(
            "auth_kit.mfa.serializers.login_factors.MFASecondStepRequestSerializer"
        )
    )
    MFA_CHANGE_METHOD_SERIALIZER: type["MFAChangeMethodSerializer"] = ImportStr(
        "auth_kit.mfa.serializers.login_factors.MFAChangeMethodSerializer"
    )
    MFA_RESEND_SERIALIZER: type["MFAResendSerializer"] = ImportStr(
        "auth_kit.mfa.serializers.login_factors.MFAResendSerializer"
    )

    # Serializer Factories
    GET_NO_MFA_LOGIN_RESPONSE_SERIALIZER: Callable[
        [], type[Serializer[dict[str, Any]]]
    ] = ImportStr(
        "auth_kit.mfa.serializers.login_factors.get_no_mfa_login_response_serializer"
    )

    MFA_FIRST_STEP_SERIALIZER_FACTORY: Callable[
        [], type[Serializer[dict[str, Any]]]
    ] = ImportStr("auth_kit.mfa.serializers.login.get_mfa_first_step_serializer")
    MFA_SECOND_STEP_SERIALIZER_FACTORY: Callable[
        [], type[Serializer[dict[str, Any]]]
    ] = ImportStr("auth_kit.mfa.serializers.login.get_mfa_second_step_serializer")

    # MFA Management Serializers
    MFA_METHOD_CONFIG_SERIALIZER: type["MFAMethodConfigSerializer"] = ImportStr(
        "auth_kit.mfa.serializers.mfa.MFAMethodConfigSerializer"
    )
    MFA_METHOD_CONFIRM_SERIALIZER: type["MFAMethodConfirmSerializer"] = ImportStr(
        "auth_kit.mfa.serializers.mfa.MFAMethodConfirmSerializer"
    )
    MFA_METHOD_CREATE_SERIALIZER: type["MFAMethodCreateSerializer"] = ImportStr(
        "auth_kit.mfa.serializers.mfa.MFAMethodCreateSerializer"
    )
    MFA_METHOD_DEACTIVATE_SERIALIZER: type["MFAMethodDeactivateSerializer"] = ImportStr(
        "auth_kit.mfa.serializers.mfa.MFAMethodDeactivateSerializer"
    )
    MFA_METHOD_DELETE_SERIALIZER: type["MFAMethodDeleteSerializer"] = ImportStr(
        "auth_kit.mfa.serializers.mfa.MFAMethodDeleteSerializer"
    )
    MFA_METHOD_PRIMARY_UPDATE_SERIALIZER: type["MFAMethodPrimaryUpdateSerializer"] = (
        ImportStr("auth_kit.mfa.serializers.mfa.MFAMethodPrimaryUpdateSerializer")
    )
    MFA_METHOD_SEND_CODE_SERIALIZER: type["MFAMethodSendCodeSerializer"] = ImportStr(
        "auth_kit.mfa.serializers.mfa.MFAMethodSendCodeSerializer"
    )

    # Field to satisfy the type checker for APISettings compatibility
    user_settings: dict[str, Any] = {}


# Dynamically generate IMPORT_STRINGS from MFASetting class
IMPORT_STRINGS = tuple(
    field
    for field in dir(MFASetting)
    if isinstance(getattr(MFASetting, field), Importable)
)


def create_api_settings_from_model(
    model_class: type,
    import_strings: tuple[str, ...],
    override_value: dict[str, Any] | None = None,
) -> MFASetting:
    """
    Create API settings instance from a model class.

    Args:
        model_class: The settings model class to use as defaults
        import_strings: Tuple of setting names that require import resolution
        override_value: Optional override values for settings

    Returns:
        Configured MySetting instance
    """
    # Get user settings from Django settings
    user_settings = getattr(settings, "AUTH_KIT", override_value)

    # Get defaults from class variables
    defaults_dict = {}
    for attr_name in dir(model_class):
        if attr_name.startswith("_"):
            continue

        attr_value = getattr(model_class, attr_name)
        # Skip methods and other non-setting attributes
        if not callable(attr_value):
            defaults_dict[attr_name] = attr_value

    # Create APISettings instance
    api_settings = APISettings(
        user_settings=user_settings,  # type: ignore
        defaults=defaults_dict,  # type: ignore
        import_strings=import_strings,
    )

    return cast(MFASetting, api_settings)


auth_kit_mfa_settings = create_api_settings_from_model(MFASetting, IMPORT_STRINGS)


def reload_api_settings(*args: Any, **kwargs: Any) -> None:
    """
    Reload API settings when Django settings change.

    Args:
        *args: Variable length argument list
        **kwargs: Arbitrary keyword arguments including 'setting' and 'value'
    """
    global auth_kit_mfa_settings  # noqa

    setting, value = kwargs["setting"], kwargs["value"]
    if setting == "AUTH_KIT":
        auth_kit_mfa_settings = create_api_settings_from_model(
            MFASetting, IMPORT_STRINGS, value
        )


setting_changed.connect(reload_api_settings)
