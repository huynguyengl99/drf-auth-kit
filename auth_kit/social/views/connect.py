"""
View for connecting social accounts to existing user accounts.

This module provides the API endpoint for authenticated users to connect
their existing account with social authentication providers.
"""

from typing import Any

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from auth_kit.social.serializers.connect import SocialConnectSerializer
from auth_kit.social.social_api_descriptions import SOCIAL_CONNECT_DESCRIPTION


class SocialConnectView(GenericAPIView[Any]):
    """
    API view for connecting social accounts to existing user accounts.

    Allows authenticated users to link their account with social
    authentication providers like Google, Facebook, GitHub, etc.
    """

    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self) -> type[SocialConnectSerializer]:
        """
        Get the serializer class for social account connection.

        Returns:
            The SocialConnectSerializer class
        """
        return SocialConnectSerializer

    @extend_schema(description=SOCIAL_CONNECT_DESCRIPTION)
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Connect a social account to the current user's account.

        Args:
            request: The HTTP request containing OAuth authorization code
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            HTTP response confirming successful account connection
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = Response(serializer.data, status=status.HTTP_200_OK)

        return response
