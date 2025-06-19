from django.urls import re_path
from django.views.generic import TemplateView

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

urlpatterns = [
    # URLs that do not require a session or valid token
    re_path(
        r"password/reset/?$", PasswordResetView.as_view(), name="rest_password_reset"
    ),
    re_path(
        r"password/reset/confirm/?$",
        PasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),
    re_path(r"login/?$", auth_kit_settings.LOGIN_VIEW.as_view(), name="rest_login"),
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
    re_path(
        r"^registration/account-confirm-email/?$",
        VerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
    re_path(
        r"account-email-verification-sent/?$",
        TemplateView.as_view(),
        name="account_email_verification_sent",
    ),
]

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
