"""
API descriptions for Auth Kit endpoints.

This module provides dynamic descriptions for OpenAPI schema generation
based on the current Auth Kit configuration settings.
"""

from auth_kit.app_settings import auth_kit_settings


def get_login_description() -> str:
    """Generate dynamic login description based on authentication type."""
    base = "Authenticate with username/email and password to obtain access tokens. "

    if auth_kit_settings.AUTH_TYPE == "jwt":
        auth_part = "Returns user details along with JWT access and refresh tokens with expiration times. "
    elif auth_kit_settings.AUTH_TYPE == "token":
        auth_part = "Returns user details along with a DRF authentication token for API access. "
    else:
        auth_part = "Returns user details along with custom authentication tokens. "

    cookie_part = ""
    if auth_kit_settings.USE_AUTH_COOKIE:
        cookie_part = (
            "Authentication cookies are set automatically for secure token storage."
        )

    return base + auth_part + cookie_part


def get_logout_description() -> str:
    """Generate dynamic logout description based on authentication type."""
    base = "Logout user and invalidate authentication tokens. "

    if auth_kit_settings.AUTH_TYPE == "jwt":
        auth_part = "Blacklists JWT refresh tokens to prevent further use. "
    elif auth_kit_settings.AUTH_TYPE == "token":
        auth_part = "Deletes the DRF authentication token from the database. "
    else:
        auth_part = "Invalidates custom authentication tokens. "

    cookie_part = ""
    if auth_kit_settings.USE_AUTH_COOKIE:
        cookie_part = "Clears authentication cookies from the browser. "

    final_part = (
        "Requires authentication to ensure only valid sessions can be logged out."
    )

    return base + auth_part + cookie_part + final_part


def get_jwt_refresh_description() -> str:
    """Generate dynamic JWT refresh description based on cookie settings."""
    base = "Generate new JWT access tokens using refresh tokens. "

    if auth_kit_settings.USE_AUTH_COOKIE:
        token_source = "Refresh tokens can be provided in request data or extracted automatically from HTTP cookies. "
        cookie_part = (
            "New tokens are automatically set in HTTP cookies for secure storage."
        )
    else:
        token_source = "Refresh tokens must be provided in the request data. "
        cookie_part = ""

    response_part = "Returns new access tokens with updated expiration times. "

    return base + token_source + response_part + cookie_part


def get_password_change_description() -> str:
    """Generate dynamic password change description based on security settings."""
    base = "Change the current user's password. Requires authentication. "

    if auth_kit_settings.OLD_PASSWORD_FIELD_ENABLED:
        security_part = "Current password verification is required for security. "
    else:
        security_part = "No current password verification required. "

    effect_part = "Successfully changing password may invalidate existing authentication sessions."

    return base + security_part + effect_part


def get_registration_description() -> str:
    """Generate dynamic registration description based on email verification settings."""
    base = "Register a new user account. "

    # Import here to avoid circular imports at module level
    try:
        from allauth.account import app_settings as allauth_settings

        if (
            allauth_settings.EMAIL_VERIFICATION
            == allauth_settings.EmailVerificationMethod.MANDATORY
        ):
            verification_part = (
                "Email verification is required - a verification email will be sent "
                "to the provided email address. The account must be verified before it can be used for login."
            )
        elif (
            allauth_settings.EMAIL_VERIFICATION
            == allauth_settings.EmailVerificationMethod.OPTIONAL
        ):
            verification_part = (
                "Email verification is optional - a verification email will be sent "
                "but the account can be used immediately for login."
            )
        else:
            verification_part = (
                "No email verification required - the account is immediately active."
            )
    except ImportError:
        # Fallback if allauth is not available
        verification_part = (
            "Email verification may be required depending on system configuration."
        )

    return base + verification_part


# Static descriptions for endpoints that don't need dynamic content
PASSWORD_RESET_DESCRIPTION = (
    "Send password reset instructions to the provided email address. "
    "If the email is registered, a secure reset link will be sent. "
    "The link expires after a limited time for security."
)

PASSWORD_RESET_CONFIRM_DESCRIPTION = (
    "Complete the password reset process using the token from the reset email. "
    "Requires the UID and token from the email along with the new password. "
    "The token is single-use and expires for security."
)

EMAIL_VERIFY_DESCRIPTION = (
    "Confirm email address using the verification key sent via email. "
    "This activates the user account and allows login access."
)

EMAIL_RESEND_DESCRIPTION = (
    "Send a new email verification message to unverified email addresses. "
    "Only works for email addresses that are registered but not yet verified."
)

USER_PROFILE_GET_DESCRIPTION = (
    "Retrieve the authenticated user's profile information including "
    "username, email, first name, and last name. Password fields are excluded."
)

USER_PROFILE_PUT_DESCRIPTION = (
    "Update the authenticated user's profile information. "
    "Allows modification of username, first name, and last name. "
    "Email field is read-only for security."
)

USER_PROFILE_PATCH_DESCRIPTION = (
    "Partially update the authenticated user's profile information. "
    "Only provided fields will be updated. Email field is read-only."
)
