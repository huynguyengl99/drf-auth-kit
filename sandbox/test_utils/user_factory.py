# pyright: reportPrivateImportUsage=false
# mypy: disable-error-code=attr-defined, allow-untyped-calls
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

import factory
from allauth.account.models import (  # pyright: ignore[reportMissingTypeStubs]
    EmailAddress,
)

from .model_factory import BaseModelFactory

UserModel: type[User] = get_user_model()  # pyright: ignore[reportAssignmentType]


class UserFactory(BaseModelFactory[User]):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")  # pyright: ignore
    email = factory.Sequence(lambda n: f"user{n}@example.com")  # pyright: ignore
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    @classmethod
    def create_with_email_address(
        cls, user_info: dict[str, Any], extra_email_info: dict[str, Any] | None = None
    ) -> tuple[User, EmailAddress]:
        user: User = UserModel.objects.create_user(**user_info)
        email_info: dict[str, Any] = {
            "email": user.email,
            "user": user,
            "verified": True,
            "primary": True,
            **(extra_email_info or {}),
        }
        email_address = EmailAddress.objects.create(**email_info)
        return user, email_address
