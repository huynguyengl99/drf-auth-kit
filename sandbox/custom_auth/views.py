from django.contrib.auth import user_logged_out
from rest_framework.request import Request
from rest_framework.response import Response

from auth_kit.app_settings import auth_kit_settings
from auth_kit.jwt_auth import set_auth_kit_cookie
from auth_kit.views import LoginView, LogoutView

from custom_auth.constants import AUTH_KNOX_TOKEN_COOKIE_NAME


class KnoxLoginView(LoginView):
    def set_custom_cookie(self, response: Response) -> None:
        set_auth_kit_cookie(
            response,
            AUTH_KNOX_TOKEN_COOKIE_NAME,
            response.data["token"],
            auth_kit_settings.AUTH_TOKEN_COOKIE_PATH,
            response.data["expiry"],
        )


class KnoxLogoutView(LogoutView):
    def logout_custom(self, request: Request, response: Response) -> None:
        request._auth.delete()
        user_logged_out.send(  # pyright: ignore[reportUnknownMemberType]
            sender=request.user.__class__, request=request, user=request.user
        )
