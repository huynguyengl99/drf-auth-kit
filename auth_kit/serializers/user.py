from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework import serializers

from allauth.account.adapter import (  # pyright: ignore[reportMissingTypeStubs]
    get_adapter,  # pyright: ignore[reportUnknownVariableType]
)

from auth_kit.serializers.login_factors import UserModel


class UserDetailsSerializer(serializers.ModelSerializer[AbstractBaseUser]):
    """
    User model w/o password
    """

    @staticmethod
    def validate_username(username: str) -> str:
        username = get_adapter().clean_username(username)  # pyright: ignore
        return username

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        extra_fields: list[str] = []
        if hasattr(UserModel, "USERNAME_FIELD"):
            extra_fields.append(UserModel.USERNAME_FIELD)
        if hasattr(UserModel, "EMAIL_FIELD"):
            extra_fields.append(UserModel.EMAIL_FIELD)
        if hasattr(UserModel, "first_name"):
            extra_fields.append("first_name")
        if hasattr(UserModel, "last_name"):
            extra_fields.append("last_name")
        model = UserModel
        fields = ("pk", *extra_fields)
        read_only_fields = ("email",)
