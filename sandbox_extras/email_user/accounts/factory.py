# pyright: reportPrivateImportUsage=false
# mypy: disable-error-code=attr-defined, allow-untyped-calls
from typing import Any

import factory
from accounts.models import User
from allauth.account.models import (  # pyright: ignore[reportMissingTypeStubs]
    EmailAddress,
)
from sandbox.test_utils.model_factory import BaseModelFactory


class UserFactory(BaseModelFactory[User]):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")  # pyright: ignore

    @classmethod
    def create_with_email_address(
        cls, user_info: dict[str, Any], extra_email_info: dict[str, Any] | None = None
    ) -> tuple[User, EmailAddress]:
        user: User = User.objects.create_user(**user_info)
        email_info: dict[str, Any] = {
            "email": user.email,
            "user": user,
            "verified": True,
            "primary": True,
            **(extra_email_info or {}),
        }
        email_address = EmailAddress.objects.create(**email_info)
        return user, email_address
