"""
Login views for Auth Kit.

This module provides login view with support for different authentication
types and cookie-based token management.
"""

from typing import Any

from django.contrib.auth import login as django_login
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.http import HttpResponseBase
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from auth_kit.api_descriptions import get_login_description
from auth_kit.app_settings import auth_kit_settings
from auth_kit.jwt_auth import set_auth_kit_cookie
from auth_kit.utils import sensitive_post_parameters_m


class LoginView(GenericAPIView[Any]):
    """
    User Authentication

    Authenticate users and obtain access tokens for API access.
    Supports both JWT and DRF token authentication based on configuration.
    """

    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = auth_kit_settings.LOGIN_SERIALIZER
    throttle_scope = "auth_kit"

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize login view.

        Args:
            **kwargs: Arbitrary keyword arguments
        """
        super().__init__(**kwargs)
        self.user: AbstractUser | AbstractBaseUser | None = None
        self.access_token: str | None = None
        self.refresh_token: str | None = None

    @sensitive_post_parameters_m
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponseBase:
        """
        Dispatch the request with sensitive parameter protection.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            HTTP response
        """
        return super().dispatch(*args, **kwargs)

    def process_login(self) -> None:
        """
        Process user login using Django's login function.
        """
        django_login(self.request, self.user)  # type: ignore[unused-ignore, arg-type]

    def create_response_with_cookies(self, validated_data: dict[str, Any]) -> Response:
        """
        Create login response with authentication cookies.

        Args:
            validated_data: Validated login data containing tokens

        Returns:
            DRF response with authentication cookies set
        """
        response = Response(validated_data, status=status.HTTP_200_OK)

        if auth_kit_settings.AUTH_TYPE == "jwt":
            set_auth_kit_cookie(
                response,
                auth_kit_settings.AUTH_JWT_COOKIE_NAME,
                validated_data["access"],
                auth_kit_settings.AUTH_JWT_COOKIE_PATH,
                validated_data["access_expiration"],
            )
            set_auth_kit_cookie(
                response,
                auth_kit_settings.AUTH_JWT_REFRESH_COOKIE_NAME,
                validated_data["refresh"],
                auth_kit_settings.AUTH_JWT_REFRESH_COOKIE_PATH,
                validated_data["refresh_expiration"],
            )
            response.data["refresh"] = ""
        elif auth_kit_settings.AUTH_TYPE == "token":
            token_cookie_expire_time = (
                timezone.now() + auth_kit_settings.AUTH_TOKEN_COOKIE_EXPIRE_TIME
                if auth_kit_settings.AUTH_TOKEN_COOKIE_EXPIRE_TIME
                else None
            )
            set_auth_kit_cookie(
                response,
                auth_kit_settings.AUTH_TOKEN_COOKIE_NAME,
                validated_data["key"],
                auth_kit_settings.AUTH_TOKEN_COOKIE_PATH,
                token_cookie_expire_time,
            )
        elif auth_kit_settings.AUTH_TYPE == "custom":
            self.set_custom_cookie(response)

        return response

    @extend_schema(description=get_login_description())
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Authenticate user and return access tokens.

        Args:
            request: The DRF request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            DRF response with login result
        """
        self.request = request
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        if auth_kit_settings.USE_AUTH_COOKIE:
            response = self.create_response_with_cookies(serializer.data)
        else:
            response = Response(serializer.data, status=status.HTTP_200_OK)

        return response

    def set_custom_cookie(self, response: Response) -> None:
        """
        Set custom authentication cookies.

        Override this method to implement custom cookie setting logic.

        Args:
            response: The DRF response object
        """
        pass
