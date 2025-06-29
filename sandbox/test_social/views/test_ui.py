"""Tests for social authentication UI views."""

from unittest.mock import MagicMock, patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from allauth.socialaccount.models import (  # pyright: ignore[reportMissingTypeStubs]
    SocialAccount,
)

from test_utils.user_factory import UserFactory


class TestSocialLoginTemplateView(APITestCase):
    @patch("auth_kit.social.views.ui.get_social_adapter")
    def test_no_providers(self, mock_adapter: MagicMock) -> None:
        mock_adapter.return_value.list_apps.return_value = []

        response = self.client.get(reverse("social_login_page"))

        assert response.status_code == 200
        assert (
            "No social providers are properly configured" in response.content.decode()
        )

    def test_renders_with_all_providers(self) -> None:
        response = self.client.get(reverse("social_login_page"))

        assert response.status_code == 200
        content = response.content.decode()
        assert "Continue with Google" in content
        assert "Continue with Facebook" in content
        assert "Continue with GitHub" in content
        assert "Continue with LinkedIn" in content


class TestSocialAccountManagementView(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create()

    def test_requires_authentication(self) -> None:
        response = self.client.get(reverse("social_management_page"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("auth_kit.social.views.ui.get_social_adapter")
    def test_no_providers(self, mock_adapter: MagicMock) -> None:
        mock_adapter.return_value.list_apps.return_value = []
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("social_management_page"))

        assert response.status_code == 200
        assert (
            "No social providers are properly configured" in response.content.decode()
        )

    def test_renders_with_all_providers(self) -> None:
        self.client.force_authenticate(user=self.user)
        SocialAccount.objects.create(user=self.user, provider="google")

        response = self.client.get(reverse("social_management_page"))

        content = response.content.decode()
        assert "Disconnect Google" in content
        assert "Connect Facebook" in content
        assert "Connect GitHub" in content
        assert "Connect LinkedIn" in content
