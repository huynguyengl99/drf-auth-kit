"""
Views package for social authentication.

This module exports all social authentication view classes for login,
account connection, and account management.

Note: UI template views (SocialLoginTemplateView, SocialAccountManagementView)
are not exported in __all__ as they are primarily intended for development
and testing purposes. These views provide HTML interfaces for social
authentication workflows but should be imported explicitly when needed:

    from auth_kit.social.views.ui import SocialLoginTemplateView, SocialAccountManagementView
"""

from .account import SocialAccountViewSet
from .connect import SocialConnectView
from .login import SocialLoginView

__all__ = [
    "SocialAccountViewSet",
    "SocialConnectView",
    "SocialLoginView",
]
