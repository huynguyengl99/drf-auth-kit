"""
Type-enhanced wrappers for django-allauth classes.

Provides better type hints for static type checking without modifying any logic.
"""

from typing import cast

from allauth.socialaccount.models import (  # pyright: ignore[reportMissingTypeStubs]
    SocialLogin as BaseSocialLogin,
)
from allauth.socialaccount.providers.oauth2.views import (  # pyright: ignore[reportMissingTypeStubs]
    OAuth2Adapter as BaseOAuth2Adapter,
)
from allauth.socialaccount.providers.openid_connect.views import (  # pyright: ignore[reportMissingTypeStubs]
    OpenIDConnectOAuth2Adapter as BaseOpenIDConnectOAuth2Adapter,
)

from auth_kit.utils import UserModelType


class SocialLogin(BaseSocialLogin):  # type: ignore[misc]
    """SocialLogin with proper type hints for user attribute."""

    user: UserModelType


class OAuth2Adapter(BaseOAuth2Adapter):  # type: ignore[misc]
    """OAuth2Adapter with explicit type hints."""

    access_token_method: str = BaseOAuth2Adapter.access_token_method
    access_token_url: str


class OpenIDConnectOAuth2Adapter(BaseOpenIDConnectOAuth2Adapter):  # type: ignore[misc]
    """OpenIDConnectOAuth2Adapter with proper type hints."""

    access_token_method: str = BaseOAuth2Adapter.access_token_method

    @property
    def access_token_url(self) -> str:
        """
        OpenID access token endpoint URL.

        Returns:
            The access token URL from the provider configuration.
        """
        return cast(str, super().access_token_url())  # pragma: no cover
