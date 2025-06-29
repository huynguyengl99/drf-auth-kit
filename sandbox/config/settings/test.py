from .dev import *  # NOQA

DEBUG = False
TEST = True

MEDIA_URL = "media-testing/"
MEDIA_ROOT = str(BASE_DIR / "media-testing/")

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "OAUTH_PKCE_ENABLED": True,
        "FETCH_USERINFO": True,
        "name": "Google",
        "APP": {
            "client_id": "test-google-client-id",
            "secret": "test-google-client-secret",
            "key": "",
        },
    },
    "github": {
        "SCOPE": [
            "user",
        ],
        "name": "GitHub",
        "APPS": [
            {
                "client_id": "test-github-client-id",
                "secret": "test-github-client-secret",
                "key": "",
            }
        ],
    },
    "facebook": {
        "METHOD": "oauth2",  # Set to 'js_sdk' to use the Facebook connect SDK
        "SCOPE": ["email", "public_profile"],
        "FIELDS": [
            "id",
            "first_name",
            "last_name",
            "name",
            "picture",
            "email",
        ],
        "EXCHANGE_TOKEN": True,
        "VERIFIED_EMAIL": False,
        "VERSION": "v13.0",
        "GRAPH_API_URL": "https://graph.facebook.com/v13.0",
        "name": "Facebook",
        "APP": {
            "client_id": "test-facebook-client-id",
            "secret": "test-facebook-client-secret",
            "key": "",
        },
    },
    "openid_connect": {
        "APPS": [
            {
                "provider_id": "linkedin",
                "name": "LinkedIn",
                "client_id": "test-linked-in-client-id",
                "secret": "test-linked-in-client-secret",
                "settings": {
                    "server_url": "https://www.linkedin.com/oauth",
                },
            }
        ]
    },
}
