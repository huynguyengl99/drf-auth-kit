"""
Serializers for social account management.

This module provides serializers for representing social account
data in REST API responses.
"""

from rest_framework import serializers

from allauth.socialaccount.models import (  # pyright: ignore[reportMissingTypeStubs]
    SocialAccount,
)


class SocialAccountSerializer(serializers.ModelSerializer[SocialAccount]):
    """
    Serializer for SocialAccount instances.

    Provides a REST API representation of django-allauth SocialAccount
    objects, including provider information and connection metadata.
    """

    class Meta:
        """Serializer metadata configuration."""

        model = SocialAccount
        fields = (
            "id",
            "provider",
            "uid",
            "last_login",
            "date_joined",
        )
