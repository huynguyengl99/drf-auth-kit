import contextlib
from collections.abc import Generator
from typing import Any, cast

from rest_framework_simplejwt.settings import api_settings


@contextlib.contextmanager
def override_jwt_settings(**settings: Any) -> Generator[None, None, None]:
    """
    Context manager to temporarily override JWT settings.

    Args:
        **settings: JWT settings to override temporarily

    Usage:
        with override_jwt_settings(ROTATE_REFRESH_TOKENS=True):
            # Code that uses the modified JWT settings
            pass
        # Settings are automatically restored
    """
    old_settings: dict[str, Any] = {}

    # Cast to dict since we know api_settings.user_settings is actually mutable
    user_settings = cast(dict[str, Any], api_settings.user_settings)

    for k, v in settings.items():
        # Save settings
        try:
            old_settings[k] = user_settings[k]
        except KeyError:
            pass

        # Install temporary settings
        user_settings[k] = v

        # Delete any cached settings
        try:
            delattr(api_settings, k)
        except AttributeError:
            pass

    try:
        yield

    finally:
        for k in settings.keys():
            # Delete temporary settings
            user_settings.pop(k)

            # Restore saved settings
            try:
                user_settings[k] = old_settings[k]
            except KeyError:
                pass

            # Delete any cached settings
            try:
                delattr(api_settings, k)
            except AttributeError:
                pass
