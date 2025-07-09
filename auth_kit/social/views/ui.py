"""
Template-based UI views for social authentication.

This module provides web interface views for social login and account
management, including provider discovery and OAuth URL generation.
"""

import secrets
from typing import Any, cast
from urllib.parse import urlencode

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from allauth.socialaccount.adapter import (  # pyright: ignore[reportMissingTypeStubs]
    get_adapter as get_social_adapter,
)
from allauth.socialaccount.models import (  # pyright: ignore[reportMissingTypeStubs]
    SocialAccount,
    SocialApp,
)
from allauth.socialaccount.providers.openid_connect.provider import (  # pyright: ignore[reportMissingTypeStubs]
    OpenIDConnectProvider,
)
from allauth.socialaccount.providers.openid_connect.views import (  # pyright: ignore[reportMissingTypeStubs]
    OpenIDConnectOAuth2Adapter,
)
from drf_spectacular.utils import extend_schema

from auth_kit.app_settings import auth_kit_settings

# Provider icon mappings (FontAwesome classes)
PROVIDER_ICONS: dict[str, str] = {
    # Major providers
    "google": "fab fa-google",
    "facebook": "fab fa-facebook-f",
    "github": "fab fa-github",
    "twitter": "fab fa-twitter",
    "twitter_oauth2": "fab fa-twitter",
    "microsoft": "fab fa-microsoft",
    "apple": "fab fa-apple",
    "discord": "fab fa-discord",
    "linkedin": "fab fa-linkedin-in",
    "linkedin_oauth2": "fab fa-linkedin-in",
    "instagram": "fab fa-instagram",
    "reddit": "fab fa-reddit-alien",
    "spotify": "fab fa-spotify",
    "twitch": "fab fa-twitch",
    "youtube": "fab fa-youtube",
    "vimeo": "fab fa-vimeo-v",
    "vimeo_oauth2": "fab fa-vimeo-v",
    "pinterest": "fab fa-pinterest-p",
    "tumblr": "fab fa-tumblr",
    "tumblr_oauth2": "fab fa-tumblr",
    "soundcloud": "fab fa-soundcloud",
    "steam": "fab fa-steam",
    "amazon": "fab fa-amazon",
    "paypal": "fab fa-paypal",
    "stripe": "fab fa-stripe",
    "dropbox": "fab fa-dropbox",
    "gitlab": "fab fa-gitlab",
    "bitbucket": "fab fa-bitbucket",
    "bitbucket_oauth2": "fab fa-bitbucket",
    "slack": "fab fa-slack",
    "telegram": "fab fa-telegram-plane",
    "whatsapp": "fab fa-whatsapp",
    "snapchat": "fab fa-snapchat-ghost",
    "tiktok": "fab fa-tiktok",
    # Regional/Asian providers
    "line": "fab fa-line",
    "weibo": "fab fa-weibo",
    "weixin": "fab fa-weixin",
    "kakao": "fab fa-kickstarter-k",  # Using K as approximation
    "naver": "fas fa-n",  # Generic N
    "baidu": "fas fa-b",  # Generic B
    "qq": "fab fa-qq",
    "vk": "fab fa-vk",
    "yandex": "fab fa-yandex",
    "mailru": "fas fa-at",
    "odnoklassniki": "fab fa-odnoklassniki",
    # Business/Professional
    "salesforce": "fab fa-salesforce",
    "hubspot": "fas fa-briefcase",
    "mailchimp": "fab fa-mailchimp",
    "shopify": "fab fa-shopify",
    "atlassian": "fab fa-atlassian",
    "asana": "fas fa-tasks",
    "trello": "fab fa-trello",
    "notion": "fas fa-sticky-note",
    "zoom": "fas fa-video",
    "quickbooks": "fab fa-quickbooks",
    # Development/Tech
    "stackexchange": "fab fa-stack-overflow",
    "stackoverflow": "fab fa-stack-overflow",
    "digitalocean": "fab fa-digital-ocean",
    "heroku": "fas fa-cloud",
    "aws": "fab fa-aws",
    "gitea": "fab fa-git-alt",
    "jupyterhub": "fas fa-code",
    "docker": "fab fa-docker",
    # Finance/Trading
    "robinhood": "fas fa-chart-line",
    "questrade": "fas fa-chart-bar",
    "coinbase": "fab fa-bitcoin",
    "stocktwits": "fas fa-dollar-sign",
    # Gaming/Entertainment
    "battlenet": "fas fa-gamepad",
    "eveonline": "fas fa-rocket",
    "lichess": "fas fa-chess",
    # Health/Fitness
    "strava": "fab fa-strava",
    "fitbit": "fas fa-heartbeat",
    "wahoo": "fas fa-bicycle",
    "trainingpeaks": "fas fa-mountain",
    # Academic/Research
    "orcid": "fab fa-orcid",
    "globus": "fas fa-globe",
    "cilogon": "fas fa-university",
    "edx": "fas fa-graduation-cap",
    "edmodo": "fas fa-chalkboard-teacher",
    # Creative/Design
    "figma": "fab fa-figma",
    "behance": "fab fa-behance",
    "dribbble": "fab fa-dribbble",
    "deviantart": "fab fa-deviantart",
    "miro": "fas fa-palette",
    # Communication/Productivity
    "box": "fas fa-box",
    "nextcloud": "fas fa-cloud",
    "hubic": "fas fa-cloud-upload-alt",
    "basecamp": "fas fa-campground",
    "evernote": "fas fa-sticky-note",
    "pocket": "fab fa-get-pocket",
    # Authentication/Identity
    "auth0": "fas fa-key",
    "okta": "fas fa-shield-alt",
    "openid": "fas fa-id-card",
    "openid_connect": "fas fa-id-card",
    "saml": "fas fa-certificate",
    "oauth2": "fas fa-key",
    "fxa": "fab fa-firefox",  # Firefox Accounts
    # Dating/Social
    "meetup": "fab fa-meetup",
    "eventbrite": "fas fa-calendar-alt",
    "patreon": "fab fa-patreon",
    # Music/Audio
    "bandcamp": "fab fa-bandcamp",
    "lastfm": "fab fa-lastfm",
    # Travel/Maps
    "foursquare": "fab fa-foursquare",
    "untappd": "fas fa-beer",
    # Other services
    "angellist": "fab fa-angellist",
    "disqus": "fas fa-comments",
    "feedly": "fas fa-rss",
    "ynab": "fas fa-piggy-bank",
    "gumroad": "fas fa-shopping-cart",
    "sharefile": "fas fa-file-alt",
    "mailcow": "fas fa-cow",
    "lemonldap": "fas fa-lemon",
    "netiq": "fas fa-network-wired",
    "authentiq": "fas fa-fingerprint",
    "exist": "fas fa-chart-pie",
    "doximity": "fas fa-user-md",
    "clever": "fas fa-lightbulb",
    "dataporten": "fas fa-database",
    "dingtalk": "fas fa-bell",
    "feishu": "fas fa-feather-alt",
    "frontier": "fas fa-rocket",
    "mediawiki": "fab fa-wikipedia-w",
    "openstreetmap": "fas fa-map",
    "agave": "fas fa-leaf",
    "bitly": "fas fa-link",
    "draugiem": "fas fa-users",
    "drip": "fas fa-tint",
    "dwolla": "fas fa-money-check-alt",
    "fivehundredpx": "fas fa-camera",
    "flickr": "fab fa-flickr",
    "twentythreeandme": "fas fa-dna",
    "xing": "fab fa-xing",
    "yahoo": "fab fa-yahoo",
    "zoho": "fas fa-briefcase",
    "windowslive": "fab fa-windows",
    "amazon_cognito": "fab fa-amazon",
    "douban": "fas fa-book",
    "daum": "fas fa-search",
}

# Default fallback styles
DEFAULT_PROVIDER_STYLE: dict[str, str] = {
    "icon": "fas fa-sign-in-alt",
}

DISPLAY_NAME_OVERRIDES = {
    "github": "GitHub",
    "linkedin": "LinkedIn",
    "linkedin_oauth2": "LinkedIn",
    "paypal": "PayPal",
    "youtube": "YouTube",
    "openid": "OpenID",
    "oauth2": "OAuth 2.0",
    "battlenet": "Battle.net",
    "stackexchange": "Stack Exchange",
    "fivehundredpx": "500px",
    "twentythreeandme": "23andMe",
    "windowslive": "Microsoft Live",
}


def get_provider_icon(provider_id: str, provider_name: str | None = None) -> str:
    """Get FontAwesome icon class for a social provider."""
    # Direct match
    if provider_id in PROVIDER_ICONS:
        return PROVIDER_ICONS[provider_id]

    # Fallback
    return DEFAULT_PROVIDER_STYLE["icon"]  # pragma: no cover


def get_provider_display_name(social_app: SocialApp) -> str:
    """Get clean display name for a social provider."""
    # Use custom name if set
    if social_app.name:
        return str(social_app.name)  # pyright: ignore[reportUnknownArgumentType]

    # Determine the key to use
    provider_key = getattr(social_app, "provider_id", None) or social_app.provider

    # Check for override
    if provider_key in DISPLAY_NAME_OVERRIDES:
        return DISPLAY_NAME_OVERRIDES[provider_key]

    # Default: clean up provider name
    return provider_key.replace("_oauth2", "").replace("_", " ").title()  # type: ignore[no-any-return]


@extend_schema(exclude=True)
class SocialLoginTemplateView(APIView):
    """
    Template view for social login page.

    Renders a web page showing all available social providers with
    OAuth login links for user authentication.
    """

    template_name = "accounts/social_login.html"
    authentication_classes = ()
    permission_classes = ()

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Render the social login template with available providers.

        Args:
            request: The Django HTTP request object

        Returns:
            Rendered HTML response with social login options
        """
        social_adapter = get_social_adapter()
        social_apps = social_adapter.list_apps(self.request)

        if not social_apps:
            return render(
                request,
                self.template_name,
                {
                    "providers": [],
                    "error": "No social providers are properly configured",
                },
            )

        all_apps = []

        for social_app in social_apps:
            provider = social_app.get_provider(self.request)

            # Generate state
            state = secrets.token_urlsafe(32)
            request.session[f"{social_app.provider}_oauth_state"] = state

            # Build OAuth URL
            default_scope = cast(list[str] | str, provider.get_default_scope())

            params = {
                "client_id": social_app.client_id,
                "redirect_uri": auth_kit_settings.SOCIAL_LOGIN_CALLBACK_URL_GENERATOR(
                    self.request, None, social_app
                ),
                "scope": (
                    " ".join(default_scope)
                    if isinstance(default_scope, list)
                    else str(default_scope)
                ),
                "response_type": "code",
                "state": state,
            }

            if isinstance(provider, OpenIDConnectProvider):
                adapter = OpenIDConnectOAuth2Adapter(request, social_app.provider_id)
                oauth_url = f"{adapter.authorize_url}?{urlencode(params)}"
                # For OpenID Connect, use provider_id for better identification
                provider_id = getattr(social_app, "provider_id", social_app.provider)
            else:
                oauth_url = (
                    f"{provider.oauth2_adapter_class.authorize_url}?{urlencode(params)}"
                )
                provider_id = social_app.provider

            # Get display name and icon
            display_name = get_provider_display_name(social_app)
            icon_class = get_provider_icon(provider_id, display_name)

            all_apps.append(
                {
                    "id": provider_id,
                    "provider": social_app.provider,  # Keep original for compatibility
                    "name": display_name,
                    "url": oauth_url,
                    "icon_class": icon_class,
                }
            )

        # Sort providers by popularity/importance
        def provider_sort_key(app: dict[str, Any]) -> int:
            """Sort providers by popularity, putting well-known providers first."""
            priority_order = [
                "google",
                "facebook",
                "github",
                "microsoft",
                "apple",
                "twitter",
                "discord",
                "linkedin_oauth2",
                "instagram",
            ]
            try:
                return priority_order.index(app["id"])
            except ValueError:
                return len(priority_order)  # Put unknown providers at the end

        all_apps.sort(key=provider_sort_key)

        context: dict[str, Any] = {
            "providers": all_apps,
        }

        return render(request, self.template_name, context)


@extend_schema(exclude=True)
class SocialAccountManagementView(APIView):
    """
    View for managing social account connections.

    Shows all available providers, indicates which ones are connected,
    and allows users to connect/disconnect social accounts.
    """

    template_name = "accounts/social_account_management.html"
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Render the social account management page.

        Args:
            request: The Django HTTP request object

        Returns:
            Rendered HTML response with account management interface
        """
        social_adapter = get_social_adapter()
        social_apps = social_adapter.list_apps(self.request)

        if not social_apps:
            return render(
                request,
                self.template_name,
                {
                    "providers": [],
                    "error": "No social providers are properly configured",
                },
            )

        # Get user's existing social accounts
        user_social_accounts = SocialAccount.objects.filter(user=request.user)
        connected_providers: dict[str, SocialAccount] = {
            account.provider: account for account in user_social_accounts
        }

        all_providers: list[dict[str, Any]] = []

        for social_app in social_apps:
            provider = social_app.get_provider(self.request)

            # Check if user is already connected to this provider
            is_connected = social_app.provider in connected_providers
            social_account = connected_providers.get(social_app.provider)

            # Generate state for OAuth
            state = secrets.token_urlsafe(32)
            request.session[f"{social_app.provider}_oauth_connect_state"] = state

            # Build OAuth URL for connection
            default_scope = cast(list[str] | str, provider.get_default_scope())

            params = {
                "client_id": social_app.client_id,
                "redirect_uri": auth_kit_settings.SOCIAL_CONNECT_CALLBACK_URL_GENERATOR(
                    self.request, None, social_app
                ),
                "scope": (
                    " ".join(default_scope)
                    if isinstance(default_scope, list)
                    else str(default_scope)
                ),
                "response_type": "code",
                "state": state,
            }

            if isinstance(provider, OpenIDConnectProvider):
                adapter = OpenIDConnectOAuth2Adapter(request, social_app.provider_id)
                connect_url = f"{adapter.authorize_url}?{urlencode(params)}"
                provider_id = getattr(social_app, "provider_id", social_app.provider)
            else:
                connect_url = (
                    f"{provider.oauth2_adapter_class.authorize_url}?{urlencode(params)}"
                )
                provider_id = social_app.provider

            # Get display name and icon
            display_name = get_provider_display_name(social_app)
            icon_class = get_provider_icon(provider_id, display_name)

            provider_data: dict[str, Any] = {
                "id": provider_id,
                "provider": social_app.provider,
                "name": display_name,
                "icon_class": icon_class,
                "is_connected": is_connected,
                "connect_url": connect_url,
                "social_account": None,
            }

            if is_connected and social_account:
                provider_data["social_account"] = {
                    "id": social_account.pk,
                    "uid": social_account.uid,
                    "last_login": social_account.last_login,
                    "date_joined": social_account.date_joined,
                }

            all_providers.append(provider_data)

        # Sort providers by connection status (connected first) then by popularity
        def provider_sort_key(provider: dict[str, Any]) -> tuple[int, Any]:
            """Sort providers by connection status and popularity."""
            # Connected providers first
            if provider["is_connected"]:
                return (0, provider["name"])

            # Then by popularity/importance
            priority_order = [
                "google",
                "facebook",
                "github",
                "microsoft",
                "apple",
                "twitter",
                "discord",
                "linkedin_oauth2",
                "instagram",
            ]
            try:
                return 1, priority_order.index(provider["id"])
            except ValueError:
                return 1, len(priority_order)

        all_providers.sort(key=provider_sort_key)

        # Count connections
        connected_count = sum(1 for p in all_providers if p["is_connected"])
        total_count = len(all_providers)

        context: dict[str, Any] = {
            "providers": all_providers,
            "connected_count": connected_count,
            "total_count": total_count,
            "user": request.user,
        }

        return render(request, self.template_name, context)
