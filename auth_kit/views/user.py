"""
User detail views for Auth Kit.

This module provides views for retrieving and updating
user profile information.
"""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db.models import QuerySet
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema,
)

from auth_kit.api_descriptions import (
    USER_PROFILE_GET_DESCRIPTION,
    USER_PROFILE_PATCH_DESCRIPTION,
    USER_PROFILE_PUT_DESCRIPTION,
)
from auth_kit.app_settings import auth_kit_settings


class UserDetailsView(RetrieveUpdateAPIView[Any]):
    """
    User Profile Management

    Retrieve and update user profile information for authenticated users.
    Allows viewing and modifying profile details like name and preferences.
    """

    serializer_class = auth_kit_settings.USER_DETAILS_SERIALIZER
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> AbstractBaseUser | AnonymousUser:
        """
        Get the current authenticated user object.

        Returns:
            The current user instance
        """
        return self.request.user

    def get_queryset(self) -> QuerySet[AbstractBaseUser]:
        """
        Get the user queryset.

        This method is sometimes called when using django-rest-swagger
        for API documentation generation.

        Returns:
            Empty user queryset
        """
        return get_user_model().objects.none()  # type: ignore[no-any-return, attr-defined, unused-ignore]

    @extend_schema(description=USER_PROFILE_GET_DESCRIPTION)
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Retrieve user profile information."""
        return super().get(request, *args, **kwargs)

    @extend_schema(description=USER_PROFILE_PUT_DESCRIPTION)
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update user profile information."""
        return super().put(request, *args, **kwargs)

    @extend_schema(description=USER_PROFILE_PATCH_DESCRIPTION)
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Partially update user profile information."""
        return super().patch(request, *args, **kwargs)
