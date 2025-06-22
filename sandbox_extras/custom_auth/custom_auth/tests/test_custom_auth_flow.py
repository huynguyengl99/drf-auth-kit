from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITransactionTestCase

from auth_kit.serializers import get_login_serializer
from sandbox.test_utils.user_factory import UserFactory

User = get_user_model()


class TestCustomAuthFlow(APITransactionTestCase):
    def setUp(self) -> None:
        self.login_data = {
            "username": "testuser",
            "password": "complexpass123",
        }
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "complexpass123",
        }

    def test_login_default_case(self) -> None:
        UserFactory.create_with_email_address(self.user_data)

        get_login_serializer.cache_clear()

        url = reverse("rest_login")
        response: Response = self.client.post(url, self.login_data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Check drf token fields
        expected_fields = {"token", "user", "expiry"}
        actual_fields = set(response.data.keys())
        assert expected_fields.issubset(actual_fields)

        # Check user data
        assert response.data["user"]["username"] == "testuser"
        assert response.data["user"]["email"] == "test@example.com"

        client_cookies = response.cookies

        # Verify cookies
        assert client_cookies["auth-knox"].value
        assert client_cookies["auth-knox"]["httponly"]
        assert client_cookies["auth-knox"]["samesite"] == "Lax"

        get_login_serializer.cache_clear()
