# pyright: reportAssignmentType=false
# mypy: disable-error-code=assignment

from collections.abc import Callable
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Literal, cast

from django.conf import settings
from django.core.signals import setting_changed
from rest_framework.authentication import BaseAuthentication
from rest_framework.serializers import Serializer
from rest_framework.settings import APISettings

if TYPE_CHECKING:
    from rest_framework.authtoken.models import Token
    from rest_framework.generics import GenericAPIView  # prevent circular import

    from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

    from auth_kit.serializers.login_factors import BaseLoginResponseSerializer
else:
    TokenObtainPairSerializer = Token = GenericAPIView = BaseLoginResponseSerializer = (
        Any
    )


class ImportStr(str):
    pass


class MySetting:
    # SERIALIZER & VIEWS dynamic load

    LOGIN_REQUEST_SERIALIZER: type[Serializer[dict[str, Any]]] = ImportStr(
        "auth_kit.serializers.login_factors.LoginRequestSerializer"
    )
    LOGIN_RESPONSE_SERIALIZER: type[BaseLoginResponseSerializer] = ImportStr(
        "auth_kit.serializers.login_factors.LoginResponseSerializer"
    )
    LOGIN_SERIALIZER: type[Serializer[dict[str, Any]]] = ImportStr(
        "auth_kit.serializers.LoginSerializer"
    )
    LOGIN_VIEW: type["GenericAPIView[Any]"] = ImportStr("auth_kit.views.LoginView")
    LOGOUT_SERIALIZER: type[Serializer[dict[str, Any]]] = ImportStr(
        "auth_kit.serializers.logout.LogoutSerializer"
    )
    LOGOUT_VIEW: type["GenericAPIView[Any]"] = ImportStr("auth_kit.views.LogoutView")
    JWT_TOKEN_CLAIMS_SERIALIZER: type[TokenObtainPairSerializer] = ImportStr(
        "rest_framework_simplejwt.serializers.TokenObtainPairSerializer"
    )
    USER_DETAILS_SERIALIZER: type[Serializer[dict[str, Any]]] = ImportStr(
        "auth_kit.serializers.user.UserDetailsSerializer"
    )
    USER_DETAILS_VIEW: type["GenericAPIView[Any]"] = ImportStr(
        "auth_kit.views.UserDetailsView"
    )
    PASSWORD_RESET_SERIALIZER: type[Serializer[dict[str, Any]]] = ImportStr(
        "auth_kit.serializers.PasswordResetSerializer"
    )
    PASSWORD_RESET_CONFIRM_SERIALIZER: type[Serializer[dict[str, Any]]] = ImportStr(
        "auth_kit.serializers.PasswordResetConfirmSerializer"
    )
    PASSWORD_CHANGE_SERIALIZER: type[Serializer[dict[str, Any]]] = ImportStr(
        "auth_kit.serializers.PasswordChangeSerializer"
    )
    REGISTER_SERIALIZER: type[Serializer[dict[str, Any]]] = ImportStr(
        "auth_kit.serializers.RegisterSerializer"
    )

    # PASSWORD CHANGE/RESET CONFIGURATIONS
    PASSWORD_RESET_CONFIRM_URL: str | None = None
    PASSWORD_RESET_URL_GENERATOR: Callable[..., str] = ImportStr(
        "auth_kit.forms.password_reset_url_generator"
    )
    OLD_PASSWORD_FIELD_ENABLED: bool = False

    # REGISTRATION CONFIGURATIONS
    REGISTER_EMAIL_CONFIRM_URL: str | None = None
    GET_EMAIL_VERIFICATION_URL_FUNC: Callable[..., str] = ImportStr(
        "auth_kit.views.registration.get_email_verification_url"
    )
    SEND_VERIFY_EMAIL_FUNC: Callable[..., None] = ImportStr(
        "auth_kit.views.registration.send_verify_email"
    )

    # Auth type setup
    AUTH_TYPE: Literal["jwt", "token", "custom"] = "jwt"  # jwt | token | custom
    USE_AUTH_COOKIE: bool = True
    SESSION_LOGIN: bool = False

    # Auth using drf Token
    AUTH_TOKEN_MODEL: Token = ImportStr("rest_framework.authtoken.models.Token")
    AUTH_TOKEN_COOKIE_NAME: str = "auth-token"
    AUTH_TOKEN_COOKIE_PATH: str = "/"
    AUTH_TOKEN_COOKIE_EXPIRE_TIME: timedelta = timedelta(days=1)

    # Auth using jwt
    AUTH_JWT_COOKIE_NAME: str = "auth-jwt"
    AUTH_JWT_COOKIE_PATH: str = "/"
    AUTH_JWT_REFRESH_COOKIE_NAME: str = "auth-refresh-jwt"
    AUTH_JWT_REFRESH_COOKIE_PATH: str = "/"

    AUTH_COOKIE_SECURE: bool = False
    AUTH_COOKIE_HTTPONLY: bool = True
    AUTH_COOKIE_SAMESITE: Literal["Lax", "Strict", "None"] = "Lax"
    AUTH_COOKIE_DOMAIN: str | None = None

    # Custom auth
    CUSTOM_LOGIN_RESPONSE_SERIALIZER: type[Serializer[dict[str, Any]]] = ImportStr(
        "auth_kit.serializers.login_factors.BaseLoginResponseSerializer"
    )
    CUSTOM_LOGOUT_SERIALIZER: type[Serializer[dict[str, Any]]] = ImportStr(
        "auth_kit.serializers.logout.AuthKitLogoutSerializer"
    )
    CUSTOM_AUTHENTICATION: type[BaseAuthentication] = ImportStr(
        "auth_kit.authentication.AuthKitCookieAuthentication"
    )

    # Field to satisfy the type checker for APISettings compatibility
    user_settings: dict[str, Any] = {}


# Dynamically generate IMPORT_STRINGS from MySetting class
IMPORT_STRINGS = tuple(
    field
    for field in dir(MySetting)
    if isinstance(getattr(MySetting, field), ImportStr)
)


def create_api_settings_from_model(
    model_class: type,
    import_strings: tuple[str, ...],
    override_value: dict[str, Any] | None = None,
) -> MySetting:
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

    return cast(MySetting, api_settings)


auth_kit_settings = create_api_settings_from_model(MySetting, IMPORT_STRINGS)


def reload_api_settings(*args: Any, **kwargs: Any) -> None:
    global auth_kit_settings  # noqa

    setting, value = kwargs["setting"], kwargs["value"]
    if setting == "AUTH_KIT":
        auth_kit_settings = create_api_settings_from_model(
            MySetting, IMPORT_STRINGS, value
        )


setting_changed.connect(reload_api_settings)  # pyright: ignore[reportUnknownMemberType]
