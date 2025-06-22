from django.urls import include, path

from sandbox.test_utils.drf_spectacular_utils import assert_schema, generate_schema


def test_auth_kit_knox_token():
    urlpatterns = [
        path("auth/", include("auth_kit.urls")),
    ]
    schema = generate_schema(None, patterns=urlpatterns)
    assert_schema(schema, "../sandbox_extras/email_user/tests/auth_kit_email_user.yml")
