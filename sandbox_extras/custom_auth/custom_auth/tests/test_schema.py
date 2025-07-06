from django.urls import include, path

from auth_kit.test_utils import override_auth_kit_settings
from sandbox.test_utils.drf_spectacular_utils import assert_schema, generate_schema
from sandbox.test_utils.urls import reload_necessary_modules_and_get_urls


def test_auth_kit_knox_token():
    urls = reload_necessary_modules_and_get_urls()

    urlpatterns = [
        path("auth/", include(urls)),
    ]
    schema = generate_schema(None, patterns=urlpatterns)
    assert_schema(
        schema, "../sandbox_extras/custom_auth/custom_auth/tests/auth_kit_knox.yml"
    )


@override_auth_kit_settings(USE_MFA=True)
def test_auth_kit_knox_token_with_mfa():
    urls = reload_necessary_modules_and_get_urls()
    urlpatterns = [
        path("auth/", include(urls)),
    ]
    schema = generate_schema(None, patterns=urlpatterns)
    assert_schema(
        schema,
        "../sandbox_extras/custom_auth/custom_auth/tests/auth_kit_knox_with_mfa.yml",
    )
