from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db.models import QuerySet
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from auth_kit.app_settings import auth_kit_settings


class UserDetailsView(RetrieveUpdateAPIView[Any]):
    """
    Reads and updates UserModel fields
    Accepts GET, PUT, PATCH methods.

    Default accepted fields: username, first_name, last_name
    Default display fields: pk, username, email, first_name, last_name
    Read-only fields: pk, email

    Returns UserModel fields.
    """

    serializer_class = auth_kit_settings.USER_DETAILS_SERIALIZER
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> AbstractBaseUser | AnonymousUser:
        return self.request.user

    def get_queryset(self) -> QuerySet[AbstractBaseUser]:
        """
        Adding this method since it is sometimes called when using
        django-rest-swagger
        """
        return get_user_model().objects.none()  # type: ignore[no-any-return, attr-defined, unused-ignore]
