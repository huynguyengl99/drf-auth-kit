import re
import uuid

from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from accounts.factories import UserFactory
from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress, get_emailconfirmation_model
from allauth.account.utils import user_pk_to_url_str

User = get_user_model()
EmailConfirmationModel = get_emailconfirmation_model()


class TestIdentifierAuthFlows(APITestCase):
    """Test authentication flows for identifier-based user model"""

    def setUp(self) -> None:
        self.identifier = str(uuid.uuid4())
        self.user_data = {
            "identifier": self.identifier,
            "email": "test@example.com",
            "password": "complexpass123",
        }

    def test_login_with_identifier_success(self) -> None:
        """Test successful login with identifier"""
        UserFactory.create_with_email_address(self.user_data)

        login_data = {
            "identifier": self.identifier,
            "password": "complexpass123",
        }

        url = reverse("rest_login")
        response: Response = self.client.post(url, login_data, format="json")

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

        # Check user data - should have identifier and email
        user_data = response.data["user"]
        assert user_data["identifier"] == self.identifier
        assert user_data["email"] == "test@example.com"
        assert "username" not in user_data  # Username should not be present
        assert "pk" in user_data

    def test_login_with_invalid_identifier(self) -> None:
        """Test login with invalid identifier credentials"""
        UserFactory.create_with_email_address(self.user_data)

        login_data = {
            "identifier": self.identifier,
            "password": "wrongpassword",
        }

        url = reverse("rest_login")
        response: Response = self.client.post(url, login_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Unable to log in" in str(response.data)

    def test_register_with_identifier_and_email(self) -> None:
        """Test user registration with identifier and email"""
        new_identifier = str(uuid.uuid4())

        registration_data = {
            "identifier": new_identifier,
            "email": "newuser@example.com",
            "password1": "complexpass123",
            "password2": "complexpass123",
        }

        url = reverse("rest_register")
        response: Response = self.client.post(url, registration_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "Verification e-mail sent" in response.data["detail"]

        # Verify user was created with provided identifier
        user_exists = User.objects.filter(identifier=new_identifier).exists()
        assert user_exists is True

        user = User.objects.get(identifier=new_identifier)
        assert user.email == "newuser@example.com"
        assert user.identifier == new_identifier
        assert user.username is None  # Username should be None
        assert user.is_active is True

        # Verify email address record
        email_address = EmailAddress.objects.get(user=user)
        assert email_address.email == "newuser@example.com"
        assert not email_address.verified  # Should be unverified initially

        # Verify verification email was sent
        assert len(mail.outbox) == 1
        verification_email = mail.outbox[0]
        assert verification_email.to == ["newuser@example.com"]
        assert "confirm" in verification_email.subject.lower()

    def test_email_verification_success(self) -> None:
        """Test successful email verification with identifier-based user"""
        # Create user with unverified email
        user, email_address = UserFactory.create_with_email_address(
            self.user_data, {"verified": False}
        )

        # Create email confirmation
        confirmation = EmailConfirmationModel.create(email_address)

        url = reverse("rest_verify_email")
        data = {"key": confirmation.key}
        response: Response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "ok"

        # Verify email is now verified
        email_address.refresh_from_db()
        assert email_address.verified

    def test_password_reset_request(self) -> None:
        """Test password reset request with identifier-based user"""
        user, _ = UserFactory.create_with_email_address(self.user_data)

        url = reverse("rest_password_reset")
        data = {"email": "test@example.com"}
        response: Response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Password reset e-mail has been sent."

        # Check that reset email was sent
        assert len(mail.outbox) == 1
        reset_email = mail.outbox[0]
        assert reset_email.to == ["test@example.com"]
        assert "password reset" in reset_email.subject.lower()

        # Verify email contains reset URL with uid and token
        email_body = reset_email.body
        assert "password" in email_body.lower()

        # Extract URL parameters for confirmation test
        url_pattern = r"uid=([a-zA-Z0-9]+).*token=([a-zA-Z0-9\-]+)"
        matches = re.search(url_pattern, email_body)
        assert matches is not None

        # Store for potential use in confirmation test
        self.reset_uid = matches.group(1)
        self.reset_token = matches.group(2)

    def test_password_reset_confirm_success(self) -> None:
        """Test successful password reset confirmation with identifier-based user"""
        user, _ = UserFactory.create_with_email_address(self.user_data)

        # Generate valid uid and token
        uid = user_pk_to_url_str(user)
        token = default_token_generator.make_token(user)

        url = reverse("rest_password_reset_confirm")
        data = {
            "uid": uid,
            "token": token,
            "new_password1": "newcomplexpass456",
            "new_password2": "newcomplexpass456",
        }

        response: Response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["detail"] == "Password has been reset with the new password."
        )

        # Verify password was actually changed
        user.refresh_from_db()
        assert user.check_password("newcomplexpass456")
        assert not user.check_password("complexpass123")

    def test_password_change_authenticated_user(self) -> None:
        """Test password change for authenticated identifier-based user"""
        user, _ = UserFactory.create_with_email_address(self.user_data)
        self.client.force_authenticate(user=user)

        url = reverse("rest_password_change")
        data = {
            "new_password1": "newnewcomplexpass789",
            "new_password2": "newnewcomplexpass789",
        }

        response: Response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "New password has been saved."

        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password("newnewcomplexpass789")
        assert not user.check_password("complexpass123")

    def test_user_profile_retrieval(self) -> None:
        """Test retrieving user profile for identifier-based user"""
        user, _ = UserFactory.create_with_email_address(self.user_data)
        self.client.force_authenticate(user=user)

        url = reverse("rest_user_details")
        response: Response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

        user_data = response.data
        assert user_data["identifier"] == self.identifier
        assert user_data["email"] == "test@example.com"
        assert user_data["pk"] == user.pk
        assert "username" not in user_data  # Username should not be present

    def test_user_profile_update(self) -> None:
        """Test updating user profile for identifier-based user"""
        user, _ = UserFactory.create_with_email_address(self.user_data)
        user.first_name = "John"
        user.last_name = "Doe"
        user.save()

        self.client.force_authenticate(user=user)

        url = reverse("rest_user_details")
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
        }

        response: Response = self.client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify changes
        user.refresh_from_db()
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"
        assert response.data["first_name"] == "Jane"
        assert response.data["last_name"] == "Smith"
        # Identifier should remain unchanged
        assert user.identifier == self.identifier
        assert response.data["identifier"] == self.identifier

    def test_login_with_nonexistent_identifier(self) -> None:
        """Test login with non-existent identifier"""
        login_data = {
            "identifier": str(uuid.uuid4()),  # Random non-existent identifier
            "password": "complexpass123",
        }

        url = reverse("rest_login")
        response: Response = self.client.post(url, login_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Unable to log in" in str(response.data)

    def test_user_details_serialization(self) -> None:
        """Test that user details serialization includes identifier field"""
        user, _ = UserFactory.create_with_email_address(self.user_data)
        self.client.force_authenticate(user=user)

        # Login to get user details in response
        login_data = {
            "identifier": self.identifier,
            "password": "complexpass123",
        }

        url = reverse("rest_login")
        response: Response = self.client.post(url, login_data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify user details structure in login response
        user_data = response.data["user"]
        assert "identifier" in user_data
        assert user_data["identifier"] == self.identifier
        assert user_data["email"] == "test@example.com"
        assert "pk" in user_data
