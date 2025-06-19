from typing import Any

from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from auth_kit.app_settings import auth_kit_settings
from auth_kit.jwt_auth import unset_jwt_cookies, unset_token_cookie


class LogoutView(GenericAPIView[Any]):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """

    permission_classes = (IsAuthenticated,)
    throttle_scope = "auth_kit"
    serializer_class = auth_kit_settings.LOGOUT_SERIALIZER

    def initial(self, request: Request, *args: Any, **kwargs: Any) -> None:
        super().initial(request, *args, **kwargs)
        cookie_name = auth_kit_settings.AUTH_JWT_REFRESH_COOKIE_NAME

        if cookie_name and cookie_name in request.COOKIES:
            self.request.data["refresh"] = request.COOKIES.get(cookie_name)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self.logout(request)

    def logout_jwt(self, request: Request, response: Response) -> None:
        if auth_kit_settings.USE_AUTH_COOKIE:
            unset_jwt_cookies(response)

        if "rest_framework_simplejwt.token_blacklist" in settings.INSTALLED_APPS:
            try:
                token = RefreshToken(None)
                if auth_kit_settings.USE_AUTH_COOKIE:
                    try:
                        token = RefreshToken(
                            request.COOKIES[  # type: ignore
                                auth_kit_settings.AUTH_JWT_REFRESH_COOKIE_NAME
                            ]
                        )
                    except KeyError:
                        response.data = {
                            "detail": _(
                                "Refresh token was not included in cookie data."
                            )
                        }
                        response.status_code = status.HTTP_401_UNAUTHORIZED
                else:
                    try:
                        token = RefreshToken(request.data["refresh"])
                    except KeyError:
                        response.data = {
                            "detail": _(
                                "Refresh token was not included in request data."
                            )
                        }
                        response.status_code = status.HTTP_401_UNAUTHORIZED

                token.blacklist()
            except TokenError as error:
                response.data = {"detail": _(str(error))}
                response.status_code = status.HTTP_400_BAD_REQUEST
                return
            except (AttributeError, TypeError):
                response.data = {"detail": _("An error has occurred.")}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def logout(self, request: Request) -> Response:
        if auth_kit_settings.SESSION_LOGIN:
            django_logout(request)

        response = Response(
            {"detail": _("Successfully logged out.")},
            status=status.HTTP_200_OK,
        )

        if auth_kit_settings.AUTH_TYPE == "jwt":
            self.logout_jwt(request, response)
        elif auth_kit_settings.AUTH_TYPE == "token":
            try:
                request.user.auth_token.delete()  # type: ignore[union-attr]
            except (AttributeError, ObjectDoesNotExist):
                pass
            if auth_kit_settings.USE_AUTH_COOKIE:
                unset_token_cookie(response)
        else:
            self.logout_custom(request, response)
        return response

    def logout_custom(self, request: Request, response: Response) -> None:
        pass
