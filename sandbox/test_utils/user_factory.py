from typing import Any

from django.contrib.auth.models import User

from allauth.account.models import EmailAddress

from test_utils.factory import BaseModelFactory


class UserFactory(BaseModelFactory[User]):
    @classmethod
    def create_with_email_address(
        cls, user_info: dict[str, Any], extra_email_info: dict[str, Any] | None = None
    ) -> tuple[User, EmailAddress]:
        user = User.objects.create_user(**user_info)
        email_info = {
            "email": user.email,
            "user": user,
            "verified": True,
            "primary": True,
            **(extra_email_info or {}),
        }
        email_address = EmailAddress.objects.create(**email_info)
        return user, email_address
