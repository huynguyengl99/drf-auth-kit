"""
API descriptions for Auth Kit MFA endpoints.

This module provides dynamic descriptions for OpenAPI schema generation
of MFA-related endpoints based on Auth Kit configuration settings.
"""

from django.utils.translation import gettext_lazy as _

from auth_kit.app_settings import auth_kit_settings
from auth_kit.mfa.mfa_settings import auth_kit_mfa_settings


def get_mfa_login_first_step_description() -> str:
    """Generate dynamic first step login description based on MFA settings."""
    base = _(
        "First step of MFA-enabled authentication. Validates credentials and initiates MFA flow. "
    )

    if auth_kit_settings.AUTH_TYPE == "jwt":
        auth_part = _(
            "Returns ephemeral token for MFA verification or complete JWT tokens if MFA is disabled. "
        )
    elif auth_kit_settings.AUTH_TYPE == "token":
        auth_part = _(
            "Returns ephemeral token for MFA verification or complete DRF tokens if MFA is disabled. "
        )
    else:
        auth_part = _(
            "Returns ephemeral token for MFA verification or complete custom tokens if MFA is disabled. "
        )

    mfa_part = _("MFA code expires in %(seconds)s seconds. ") % {
        "seconds": auth_kit_mfa_settings.MFA_EPHEMERAL_TOKEN_EXPIRY
    }

    return str(base) + str(auth_part) + str(mfa_part)


def get_mfa_login_second_step_description() -> str:
    """Generate dynamic second step login description based on authentication type."""
    base = _(
        "Complete MFA authentication using verification code and ephemeral token. "
    )

    if auth_kit_settings.AUTH_TYPE == "jwt":
        auth_part = _(
            "Returns user details along with JWT access and refresh tokens with expiration times. "
        )
    elif auth_kit_settings.AUTH_TYPE == "token":
        auth_part = _(
            "Returns user details along with a DRF authentication token for API access. "
        )
    else:
        auth_part = _("Returns user details along with custom authentication tokens. ")

    cookie_part = ""
    if auth_kit_settings.USE_AUTH_COOKIE:
        cookie_part = _(
            "Authentication cookies are set automatically for secure token storage. "
        )

    verification_part = _("Supports both TOTP codes and backup codes for verification.")

    return str(base) + str(auth_part) + str(cookie_part) + str(verification_part)


def get_mfa_login_change_method_description() -> str:
    """Generate description for MFA method change during login."""
    base = _("Switch to a different MFA method during authentication flow. ")

    requirements = _("Requires valid ephemeral token from first step authentication. ")

    expiry_part = _("New ephemeral token expires in %(seconds)s seconds.") % {
        "seconds": auth_kit_mfa_settings.MFA_EPHEMERAL_TOKEN_EXPIRY
    }

    return str(base) + str(requirements) + str(expiry_part)


def get_mfa_login_resend_description() -> str:
    """Generate description for MFA code resend functionality."""
    base = _("Resend MFA verification code using existing ephemeral token. ")

    handlers_part = _(
        "Only applicable for methods that require code dispatch (e.g., email). "
    )

    expiry_part = _("New ephemeral token expires in %(seconds)s seconds.") % {
        "seconds": auth_kit_mfa_settings.MFA_EPHEMERAL_TOKEN_EXPIRY
    }

    return str(base) + str(handlers_part) + str(expiry_part)


# MFA Method Management Descriptions
MFA_METHOD_LIST_DESCRIPTION = _(
    "List all available MFA methods with their setup and activation status. "
    "Shows which methods are configured, active, and set as primary."
)

MFA_METHOD_CREATE_DESCRIPTION = _(
    "Initialize a new MFA method setup. Creates the method with backup codes "
    "and returns setup instructions (e.g., QR code for authenticator apps). "
    "Method must be confirmed before activation."
)

MFA_METHOD_CONFIRM_DESCRIPTION = _(
    "Confirm and activate a newly created MFA method using verification code. "
    "Automatically sets as primary method if no other primary method exists. "
    "Required before the method can be used for authentication."
)

MFA_METHOD_DEACTIVATE_DESCRIPTION = _(
    "Deactivate an active MFA method. Requires verification code from the method itself. "
    "Cannot deactivate primary methods - set another method as primary first."
)


def get_mfa_method_primary_description() -> str:
    """Generate dynamic description for setting primary MFA method."""
    base = _(
        "Set an active MFA method as the primary authentication method. "
        "Primary method is used by default during login flow. "
    )

    verification_part = ""
    if auth_kit_mfa_settings.MFA_UPDATE_PRIMARY_METHOD_REQUIRED_PRIMARY_CODE:
        verification_part = _(
            "Requires verification code from current primary method. "
        )

    ending = _("Only one method can be primary at a time.")

    return str(base) + str(verification_part) + str(ending)


MFA_METHOD_SEND_CODE_DESCRIPTION = _(
    "Send verification code for methods that support code dispatch. "
    "Useful for testing method configuration or manual code requests."
)


def get_mfa_method_delete_description() -> str:
    """Generate dynamic description for MFA method deletion."""
    base = _("Permanently delete an MFA method. ")

    restrictions = []

    if auth_kit_mfa_settings.MFA_PREVENT_DELETE_ACTIVE_METHOD:
        restrictions.append(_("Cannot delete active methods. "))

    if auth_kit_mfa_settings.MFA_PREVENT_DELETE_PRIMARY_METHOD:
        restrictions.append(_("Cannot delete primary methods. "))

    if auth_kit_mfa_settings.MFA_DELETE_ACTIVE_METHOD_REQUIRE_CODE:
        restrictions.append(_("Requires verification code for active methods. "))

    ending = _("This action cannot be undone.")

    restrictions_text = "".join(str(r) for r in restrictions)

    return str(base) + restrictions_text + str(ending)
