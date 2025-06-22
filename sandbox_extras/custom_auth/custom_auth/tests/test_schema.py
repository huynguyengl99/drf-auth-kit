from django.urls import include, path

from sandbox.test_utils.drf_spectacular_utils import assert_schema, generate_schema


def test_auth_kit_knox_token():
    urlpatterns = [
        path("auth/", include("auth_kit.urls")),
    ]
    schema = generate_schema(None, patterns=urlpatterns)
    assert_schema(
        schema, "../sandbox_extras/custom_auth/custom_auth/tests/auth_kit_knox.yml"
    )
