"""
API descriptions for Social Auth Kit endpoints.

This module provides dynamic descriptions for social authentication OpenAPI schema generation
based on the current Auth Kit configuration settings.
"""

from functools import partial
from typing import TYPE_CHECKING

from django.utils.functional import lazy
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from auth_kit.api_descriptions import (
    get_auth_cookie_description,
    get_auth_type_description,
)

if TYPE_CHECKING:  # pragma: no cover
    from django.utils.functional import _StrOrPromise
else:
    _StrOrPromise = str


def get_social_login_description(
    provider_name: str = "social provider",
) -> _StrOrPromise:
    """Generate dynamic social login description based on authentication type."""
    base = _(
        "Authenticate with %(provider)s using OAuth2/OpenID Connect authorization code to obtain access tokens."
    ) % {"provider": provider_name}
    # Reuse existing functions from api_descriptions
    auth_part = get_auth_type_description()
    cookie_part = get_auth_cookie_description()

    if cookie_part:
        return format_lazy(
            "{} {} {}",
            base,
            auth_part,
            cookie_part,
        )
    else:
        return format_lazy("{} {}", base, auth_part)


def get_social_connect_description(
    provider_name: str = "social provider",
) -> _StrOrPromise:
    """Generate social account connection description."""
    base = _(
        "Connect a %(provider)s account to the current user's account. "
        "This allows the user to login using their existing %(provider)s account in the future."
    ) % {"provider": provider_name}

    requirements = _(
        "Requires authentication and a valid OAuth2/OpenID Connect authorization code from %(provider)s."
    ) % {"provider": provider_name}

    result = _(
        "On success, the %(provider)s account is linked and can be used for future logins."
    ) % {"provider": provider_name}

    return format_lazy(
        "{} {} {}",
        base,
        requirements,
        result,
    )


def get_lazy_social_login_description(provider_name: str) -> _StrOrPromise:
    """Get a lazy version of social login description for a specific provider."""
    return lazy(partial(get_social_login_description, provider_name), str)()


def get_lazy_social_connect_description(provider_name: str) -> _StrOrPromise:
    """Get a lazy version of social connect description for a specific provider."""
    return lazy(partial(get_social_connect_description, provider_name), str)()


# Social Account Management descriptions
SOCIAL_ACCOUNT_LIST_DESCRIPTION = _(
    "List all social accounts connected to the current user. "
    "Shows account details including provider, UID, and connection dates."
)

SOCIAL_ACCOUNT_DELETE_DESCRIPTION = _(
    "Disconnect a social account from the current user. "
    "Removes the social account connection and prevents future logins via that provider. "
    "Requires authentication and the account must belong to the current user."
)

# Static descriptions for social endpoints
SOCIAL_LOGIN_DESCRIPTION = lazy(get_social_login_description, str)()
SOCIAL_CONNECT_DESCRIPTION = lazy(get_social_connect_description, str)()
