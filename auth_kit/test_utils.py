"""
Test utilities for Auth Kit.

This module provides testing utilities for temporarily overriding Auth Kit
settings during test execution. Supports both synchronous and asynchronous
test functions with automatic cleanup of modified settings.
"""

import contextlib
import functools
import inspect
from collections.abc import Callable, Iterator
from typing import Any, TypeVar, cast

from auth_kit.app_settings import auth_kit_settings
from auth_kit.mfa.mfa_settings import auth_kit_mfa_settings

T = TypeVar("T", bound=Callable[..., Any])


def override_auth_kit_settings(**settings: Any) -> Callable[[T], T]:
    """
    Decorator for overriding auth kit settings for the duration of a test function.
    Works with both sync and async functions.

    Usage:
        @override_auth_kit_settings(SEND_COMPLETION=True)
        async def test_something_async():
            ...

        @override_auth_kit_settings(SEND_COMPLETION=True)
        def test_something_sync():
            ...
    """

    def decorator(func: T) -> T:
        """
        Inner decorator function that wraps the target function.

        Selects the appropriate wrapper based on whether the target function
        is synchronous or asynchronous. Both wrappers establish a settings context
        around the function execution.

        Args:
            func: The function to be wrapped, can be either sync or async

        Returns:
            A wrapped version of the function that applies temporary settings
        """
        if inspect.iscoroutinefunction(func):
            # Handle async functions
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                """
                Wrapper for asynchronous functions.

                Creates a settings context and awaits the wrapped coroutine function.

                Args:
                    *args: Positional arguments to pass to the wrapped function
                    **kwargs: Keyword arguments to pass to the wrapped function

                Returns:
                    The result of the wrapped coroutine function
                """
                with settings_context(**settings):
                    return await func(*args, **kwargs)

            return cast(T, async_wrapper)
        else:
            # Handle synchronous functions
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                """
                Wrapper for synchronous functions.

                Creates a settings context and calls the wrapped function.

                Args:
                    *args: Positional arguments to pass to the wrapped function
                    **kwargs: Keyword arguments to pass to the wrapped function

                Returns:
                    The result of the wrapped function
                """
                with settings_context(**settings):
                    return func(*args, **kwargs)

            return cast(T, sync_wrapper)

    return decorator


@contextlib.contextmanager
def settings_context(**settings: Any) -> Iterator[None]:  # noqa
    """Context manager for overriding auth kit settings temporarily."""
    # Initialize user_settings if it doesn't exist

    if not hasattr(auth_kit_settings, "user_settings"):
        auth_kit_settings.user_settings = {}
        auth_kit_mfa_settings.user_settings = {}

    # Save original settings
    old_settings = {}
    for key in settings:
        old_settings[key] = auth_kit_settings.user_settings.get(
            key
        ) or auth_kit_mfa_settings.user_settings.get(key)

    # Apply new settings and clear cached properties
    for key, value in settings.items():
        if hasattr(auth_kit_settings, key):
            auth_kit_settings.user_settings[key] = value
            with contextlib.suppress(AttributeError):
                delattr(auth_kit_settings, key)
        elif hasattr(auth_kit_mfa_settings, key):
            auth_kit_mfa_settings.user_settings[key] = value
            with contextlib.suppress(AttributeError):
                delattr(auth_kit_mfa_settings, key)

    try:
        yield
    finally:
        # Restore original settings
        for key in settings:
            if old_settings[key] is not None:
                if hasattr(auth_kit_settings, key):
                    auth_kit_settings.user_settings[key] = old_settings[key]
                elif hasattr(auth_kit_mfa_settings, key):
                    auth_kit_mfa_settings.user_settings[key] = old_settings[key]
            elif hasattr(auth_kit_settings, key):
                auth_kit_settings.user_settings.pop(key, None)
            elif hasattr(auth_kit_mfa_settings, key):
                auth_kit_mfa_settings.user_settings.pop(key, None)

            # Clear cached properties again
            with contextlib.suppress(AttributeError):
                if hasattr(auth_kit_settings, key):
                    delattr(auth_kit_settings, key)
                elif hasattr(auth_kit_mfa_settings, key):
                    delattr(auth_kit_mfa_settings, key)
