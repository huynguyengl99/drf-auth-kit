from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from sandbox.test_utils.user_factory import UserFactory

User = get_user_model()


class TestLoginView(APITestCase):
    def setUp(self) -> None:
        self.login_data = {
            "email": "test@example.com",
            "password": "complexpass123",
        }
        self.user_data = {
            "email": "test@example.com",
            "password": "complexpass123",
        }

    def test_login_default_case(self) -> None:
        UserFactory.create_with_email_address(self.user_data)

        url = reverse("rest_login")
        response: Response = self.client.post(url, self.login_data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Check JWT token fields
        expected_fields = {
            "access",
            "refresh",
            "access_expiration",
            "refresh_expiration",
            "user",
        }
        actual_fields = set(response.data.keys())
        assert expected_fields.issubset(actual_fields)

        # Check user data
        assert not hasattr(response.data["user"], "username")
        assert response.data["user"]["email"] == "test@example.com"

        # Verify tokens are strings
        assert isinstance(response.data["access"], str)
        assert isinstance(response.data["refresh"], str)

        # Verify refresh token is remove due because of moving to secure http only cookie
        assert response.data["refresh"] == ""

        client_cookies = response.cookies

        # Verify cookies
        assert client_cookies["auth-jwt"].value
        assert client_cookies["auth-jwt"]["httponly"]
        assert client_cookies["auth-jwt"]["samesite"] == "Lax"
        assert client_cookies["auth-refresh-jwt"].value
        assert client_cookies["auth-refresh-jwt"]["httponly"]
        assert client_cookies["auth-refresh-jwt"]["samesite"] == "Lax"
