"""
View for social authentication login.

This module provides the API endpoint for user authentication
via social providers like Google, Facebook, GitHub, etc.
"""

from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from drf_spectacular.utils import extend_schema

from auth_kit.allauth_enhanced import OAuth2Adapter
from auth_kit.app_settings import auth_kit_settings
from auth_kit.social.social_api_descriptions import SOCIAL_LOGIN_DESCRIPTION
from auth_kit.views import LoginView


class SocialLoginView(LoginView):
    """
    API view for social authentication login.

    Handles OAuth-based authentication flows for social providers.
    Extends the base LoginView to provide social-specific functionality.
    """

    adapter_class: type[OAuth2Adapter]

    def get_serializer_class(self) -> type[Serializer[dict[str, Any]]]:
        """
        Get the serializer class for social login.

        Returns:
            The dynamically generated social login serializer class
        """
        # Extract provider name from class name (e.g., "GoogleLoginView" -> "Google")
        provider_name = self.__class__.__name__.removesuffix("LoginView")

        return auth_kit_settings.SOCIAL_LOGIN_SERIALIZER_FACTORY(provider_name)

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the social login view.

        Args:
            **kwargs: Arbitrary keyword arguments

        Raises:
            ValueError: If adapter_class is not defined on the view
        """
        super().__init__(**kwargs)
        adapter_class = getattr(self, "adapter_class", None)
        if not adapter_class:
            raise ValueError(_("adapter_class is not defined"))

    @extend_schema(description=SOCIAL_LOGIN_DESCRIPTION)
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Authenticate via social provider OAuth token.

        Args:
            request: The HTTP request containing OAuth authorization code/token
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            HTTP response with user details and authentication tokens
        """
        return super().post(request, *args, **kwargs)
