"""
URL configuration for Auth Kit authentication endpoints.

This module defines all URL patterns for authentication-related views
including login, logout, registration, password reset, and email verification.
"""

from django.urls import URLPattern, URLResolver, include, re_path

from rest_framework_simplejwt.views import TokenVerifyView

from auth_kit.views import (
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
    RefreshViewWithCookieSupport,
    RegisterView,
    ResendEmailVerificationView,
    VerifyEmailView,
)

from .app_settings import auth_kit_settings

urlpatterns: list[URLPattern | URLResolver] = [
    # URLs that do not require a session or valid token
    re_path(
        r"password/reset/?$", PasswordResetView.as_view(), name="rest_password_reset"
    ),
    re_path(
        r"password/reset/confirm/?$",
        PasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),
    # URLs that require a user to be logged in with a valid session / token.
    re_path(r"logout/?$", auth_kit_settings.LOGOUT_VIEW.as_view(), name="rest_logout"),
    re_path(
        r"user/?$",
        auth_kit_settings.USER_DETAILS_VIEW.as_view(),
        name="rest_user_details",
    ),
    re_path(
        r"password/change/?$", PasswordChangeView.as_view(), name="rest_password_change"
    ),
    re_path(r"registration/?$", RegisterView.as_view(), name="rest_register"),
    re_path(
        r"registration/verify-email/?$",
        VerifyEmailView.as_view(),
        name="rest_verify_email",
    ),
    re_path(
        r"registration/resend-email/?$",
        ResendEmailVerificationView.as_view(),
        name="rest_resend_email",
    ),
]

if not auth_kit_settings.USE_MFA:
    urlpatterns.extend(
        [
            re_path(
                r"login/?$", auth_kit_settings.LOGIN_VIEW.as_view(), name="rest_login"
            ),
        ]
    )
else:

    urlpatterns.extend([re_path("", include("auth_kit.mfa.urls"))])

if auth_kit_settings.AUTH_TYPE == "jwt":
    urlpatterns.extend(
        [
            re_path(r"token/verify/?$", TokenVerifyView.as_view(), name="token_verify"),
            re_path(
                r"token/refresh/?$",
                RefreshViewWithCookieSupport().as_view(),
                name="token_refresh",
            ),
        ]
    )
