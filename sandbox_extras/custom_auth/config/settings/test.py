from .dev import *  # NOQA

DEBUG = False
TEST = True

MEDIA_URL = "media-testing/"
MEDIA_ROOT = str(BASE_DIR / "media-testing/")

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
