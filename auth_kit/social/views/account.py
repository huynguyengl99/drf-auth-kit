"""
ViewSet for managing user's social account connections.

This module provides REST API endpoints for listing and removing
social account connections for authenticated users.
"""

from django.db.models import QuerySet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from allauth.socialaccount import signals  # pyright: ignore[reportMissingTypeStubs]
from allauth.socialaccount.models import (  # pyright: ignore[reportMissingTypeStubs]
    SocialAccount,
)
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

from auth_kit.social.serializers import SocialAccountSerializer
from auth_kit.social.social_api_descriptions import (
    SOCIAL_ACCOUNT_DELETE_DESCRIPTION,
    SOCIAL_ACCOUNT_LIST_DESCRIPTION,
)


@extend_schema_view(
    list=extend_schema(description=SOCIAL_ACCOUNT_LIST_DESCRIPTION),
    destroy=extend_schema(
        description=SOCIAL_ACCOUNT_DELETE_DESCRIPTION,
        parameters=[
            OpenApiParameter(
                name="id",
                location="path",
                required=True,
                type=int,
                description="A unique integer value identifying this social account.",
            )
        ],
    ),
)
class SocialAccountViewSet(
    mixins.ListModelMixin, mixins.DestroyModelMixin, GenericViewSet[SocialAccount]
):
    """
    ViewSet for managing social account connections.

    Provides endpoints for authenticated users to:
    - List their connected social accounts
    - Remove/disconnect social accounts
    """

    serializer_class = SocialAccountSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet[SocialAccount]:
        """
        Get social accounts for the current authenticated user.

        Returns:
            QuerySet of SocialAccount objects for the current user
        """
        return SocialAccount.objects.filter(user=self.request.user)  # type: ignore[no-any-return]

    def perform_destroy(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, instance: SocialAccount
    ) -> None:
        """
        Handle social account disconnection.

        Sends the social_account_removed signal before deleting the account
        to notify other parts of the application about the disconnection.

        Args:
            instance: The SocialAccount instance to remove
        """
        signals.social_account_removed.send(
            sender=SocialAccount,
            request=self.request,
            socialaccount=instance,
        )
        instance.delete()
