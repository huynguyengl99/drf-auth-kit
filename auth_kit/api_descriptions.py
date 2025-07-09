"""
API descriptions for Auth Kit endpoints.

This module provides dynamic descriptions for OpenAPI schema generation
based on the current Auth Kit configuration settings.
"""

from typing import TYPE_CHECKING

from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from allauth.account import (  # pyright: ignore[reportMissingTypeStubs]
    app_settings as allauth_account_settings,
)

from auth_kit.app_settings import auth_kit_settings

if TYPE_CHECKING:  # pragma: no cover
    from django.utils.functional import _StrOrPromise
else:
    _StrOrPromise = str


def get_auth_type_description() -> _StrOrPromise:
    """Get authentication type description based on current settings."""
    if auth_kit_settings.AUTH_TYPE == "jwt":
        return _(
            "Returns user details along with JWT access and refresh tokens with expiration times."
        )
    elif auth_kit_settings.AUTH_TYPE == "token":
        return _(
            "Returns user details along with a DRF authentication token for API access."
        )
    else:
        return _("Returns user details along with custom authentication tokens.")


def get_auth_tokens_name() -> _StrOrPromise:
    """Get just the token type name for use in sentences."""
    if auth_kit_settings.AUTH_TYPE == "jwt":
        return _("JWT access and refresh tokens")
    elif auth_kit_settings.AUTH_TYPE == "token":
        return _("DRF authentication token")
    else:
        return _("custom authentication tokens")


def get_auth_cookie_description() -> _StrOrPromise:
    """Get cookie description if cookies are enabled."""
    if auth_kit_settings.USE_AUTH_COOKIE:
        return _(
            "Authentication cookies are set automatically for secure token storage."
        )
    return ""


def get_auth_invalidation_description() -> _StrOrPromise:
    """Get authentication invalidation description based on current settings."""
    if auth_kit_settings.AUTH_TYPE == "jwt":
        return _("Blacklists JWT refresh tokens to prevent further use.")
    elif auth_kit_settings.AUTH_TYPE == "token":
        return _("Deletes the DRF authentication token from the database.")
    else:
        return _("Invalidates custom authentication tokens.")


def get_cookie_clearing_description() -> _StrOrPromise:
    """Get cookie clearing description if cookies are enabled."""
    if auth_kit_settings.USE_AUTH_COOKIE:
        return _("Clears authentication cookies from the browser.")
    return ""


def get_login_description() -> _StrOrPromise:
    """Generate dynamic login description based on authentication type."""
    base = _("Authenticate with username/email and password to obtain access tokens.")
    auth_part = get_auth_type_description()
    cookie_part = get_auth_cookie_description()

    if cookie_part:
        return format_lazy("{} {} {}", base, auth_part, cookie_part)
    else:
        return format_lazy("{} {}", base, auth_part)


def get_logout_description() -> _StrOrPromise:
    """Generate dynamic logout description based on authentication type."""
    base = _("Logout user and invalidate authentication tokens.")
    auth_part = get_auth_invalidation_description()
    cookie_part = get_cookie_clearing_description()
    final_part = _(
        "Requires authentication to ensure only valid sessions can be logged out."
    )

    if cookie_part:
        return format_lazy("{} {} {} {}", base, auth_part, cookie_part, final_part)
    else:
        return format_lazy("{} {} {}", base, auth_part, final_part)


def get_jwt_refresh_description() -> _StrOrPromise:
    """Generate dynamic JWT refresh description based on cookie settings."""
    base = _("Generate new JWT access tokens using refresh tokens.")

    if auth_kit_settings.USE_AUTH_COOKIE:
        token_source = _(
            "Refresh tokens can be provided in request data or extracted automatically from HTTP cookies."
        )
        response_part = _("Returns new access tokens with updated expiration times.")
        cookie_part = _(
            "New tokens are automatically set in HTTP cookies for secure storage."
        )

        return format_lazy(
            "{} {} {} {}", base, token_source, response_part, cookie_part
        )
    else:
        token_source = _("Refresh tokens must be provided in the request data.")
        response_part = _("Returns new access tokens with updated expiration times.")

        return format_lazy("{} {} {}", base, token_source, response_part)


def get_register_description() -> _StrOrPromise:
    """Generate dynamic registration description based on email verification settings."""
    base = _("Register a new user account.")

    if (
        allauth_account_settings.EMAIL_VERIFICATION
        == allauth_account_settings.EmailVerificationMethod.MANDATORY
    ):
        verification_part = _(
            "Users must verify their email address before the account is fully activated."
        )
        return format_lazy("{} {}", base, verification_part)

    return base


# Static descriptions for endpoints that don't need dynamic content
PASSWORD_RESET_DESCRIPTION = _(
    "Send password reset instructions to the provided email address. "
    "If the email is registered, a secure reset link will be sent. "
    "The link expires after a limited time for security."
)

PASSWORD_RESET_CONFIRM_DESCRIPTION = _(
    "Complete the password reset process using the token from the reset email. "
    "Requires the UID and token from the email along with the new password. "
    "The token is single-use and expires for security."
)

PASSWORD_CHANGE_DESCRIPTION = _(
    "Change the current user's password. Requires authentication. "
)

EMAIL_VERIFY_DESCRIPTION = _(
    "Confirm email address using the verification key sent via email. "
    "This activates the user account and allows login access."
)

EMAIL_RESEND_DESCRIPTION = _(
    "Send a new email verification message to unverified email addresses. "
    "Only works for email addresses that are registered but not yet verified."
)

USER_PROFILE_GET_DESCRIPTION = _(
    "Retrieve the authenticated user's profile information including "
    "username, email, first name, and last name. Password fields are excluded."
)

USER_PROFILE_PUT_DESCRIPTION = _(
    "Update the authenticated user's profile information. "
    "Allows modification of username, first name, and last name. "
    "Email field is read-only for security."
)

USER_PROFILE_PATCH_DESCRIPTION = _(
    "Partially update the authenticated user's profile information. "
    "Only provided fields will be updated. Email field is read-only."
)
