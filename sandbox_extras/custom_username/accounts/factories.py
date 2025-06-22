import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser

from allauth.account.models import EmailAddress
from sandbox.test_utils.model_factory import BaseModelFactory

UserModel = get_user_model()


class UserFactory(BaseModelFactory[AbstractBaseUser]):
    @classmethod
    def create_with_email_address(
        cls, user_info: dict[str, Any], extra_email_info: dict[str, Any] | None = None
    ) -> tuple[AbstractBaseUser, EmailAddress]:
        # Ensure an identifier is provided or generated
        if "identifier" not in user_info:
            user_info["identifier"] = str(uuid.uuid4())

        user = UserModel.objects.create_user(**user_info)

        email_info = {
            "email": user.email,
            "user": user,
            "verified": True,
            "primary": True,
            **(extra_email_info or {}),
        }
        email_address = EmailAddress.objects.create(**email_info)
        return user, email_address
