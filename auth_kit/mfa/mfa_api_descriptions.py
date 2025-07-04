"""
API descriptions for Auth Kit MFA endpoints.

This module provides dynamic descriptions for OpenAPI schema generation
of MFA-related endpoints based on Auth Kit configuration settings.
"""

from auth_kit.app_settings import auth_kit_settings
from auth_kit.mfa.mfa_settings import auth_kit_mfa_settings


def get_mfa_login_first_step_description() -> str:
    """Generate dynamic first step login description based on MFA settings."""
    base = "First step of MFA-enabled authentication. Validates credentials and initiates MFA flow. "

    if auth_kit_settings.AUTH_TYPE == "jwt":
        auth_part = "Returns ephemeral token for MFA verification or complete JWT tokens if MFA is disabled. "
    elif auth_kit_settings.AUTH_TYPE == "token":
        auth_part = "Returns ephemeral token for MFA verification or complete DRF tokens if MFA is disabled. "
    else:
        auth_part = "Returns ephemeral token for MFA verification or complete custom tokens if MFA is disabled. "

    mfa_part = f"MFA code expires in {auth_kit_mfa_settings.MFA_EPHEMERAL_TOKEN_EXPIRY} seconds. "

    return base + auth_part + mfa_part


def get_mfa_login_second_step_description() -> str:
    """Generate dynamic second step login description based on authentication type."""
    base = "Complete MFA authentication using verification code and ephemeral token. "

    if auth_kit_settings.AUTH_TYPE == "jwt":
        auth_part = "Returns user details along with JWT access and refresh tokens with expiration times. "
    elif auth_kit_settings.AUTH_TYPE == "token":
        auth_part = "Returns user details along with a DRF authentication token for API access. "
    else:
        auth_part = "Returns user details along with custom authentication tokens. "

    cookie_part = ""
    if auth_kit_settings.USE_AUTH_COOKIE:
        cookie_part = (
            "Authentication cookies are set automatically for secure token storage. "
        )

    verification_part = "Supports both TOTP codes and backup codes for verification."

    return base + auth_part + cookie_part + verification_part


def get_mfa_change_method_description() -> str:
    """Generate description for MFA method change during login."""
    base = "Switch to a different MFA method during authentication flow. "

    requirements = "Requires valid ephemeral token from first step authentication. "

    expiry_part = f"New ephemeral token expires in {auth_kit_mfa_settings.MFA_EPHEMERAL_TOKEN_EXPIRY} seconds."

    return base + requirements + expiry_part


def get_mfa_resend_description() -> str:
    """Generate description for MFA code resend functionality."""
    base = "Resend MFA verification code using existing ephemeral token. "

    handlers_part = (
        "Only applicable for methods that require code dispatch (e.g., email). "
    )

    expiry_part = f"New ephemeral token expires in {auth_kit_mfa_settings.MFA_EPHEMERAL_TOKEN_EXPIRY} seconds."

    return base + handlers_part + expiry_part


# MFA Method Management Descriptions
MFA_METHOD_LIST_DESCRIPTION = (
    "List all available MFA methods with their setup and activation status. "
    "Shows which methods are configured, active, and set as primary."
)

MFA_METHOD_CREATE_DESCRIPTION = (
    "Initialize a new MFA method setup. Creates the method with backup codes "
    "and returns setup instructions (e.g., QR code for authenticator apps). "
    "Method must be confirmed before activation."
)

MFA_METHOD_CONFIRM_DESCRIPTION = (
    "Confirm and activate a newly created MFA method using verification code. "
    "Automatically sets as primary method if no other primary method exists. "
    "Required before the method can be used for authentication."
)

MFA_METHOD_DEACTIVATE_DESCRIPTION = (
    "Deactivate an active MFA method. Requires verification code from the method itself. "
    "Cannot deactivate primary methods - set another method as primary first."
)

MFA_METHOD_PRIMARY_DESCRIPTION = (
    "Set an active MFA method as the primary authentication method. "
    "Primary method is used by default during login flow. "
    f"{'Requires verification code from current primary method. ' if auth_kit_mfa_settings.MFA_UPDATE_PRIMARY_METHOD_REQUIRED_PRIMARY_CODE else ''}"
    "Only one method can be primary at a time."
)

MFA_METHOD_SEND_CODE_DESCRIPTION = (
    "Send verification code for methods that support code dispatch. "
    "Useful for testing method configuration or manual code requests."
)

MFA_METHOD_DELETE_DESCRIPTION = (
    "Permanently delete an MFA method. "
    f"{'Cannot delete active methods. ' if auth_kit_mfa_settings.MFA_PREVENT_DELETE_ACTIVE_METHOD else ''}"
    f"{'Cannot delete primary methods. ' if auth_kit_mfa_settings.MFA_PREVENT_DELETE_PRIMARY_METHOD else ''}"
    f"{'Requires verification code for active methods. ' if auth_kit_mfa_settings.MFA_DELETE_ACTIVE_METHOD_REQUIRE_CODE else ''}"
    "This action cannot be undone."
)
