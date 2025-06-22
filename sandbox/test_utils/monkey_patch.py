from collections.abc import Generator
from contextlib import contextmanager
from typing import Any


@contextmanager
def temporary_class_attribute(
    cls: type, attribute_name: str, new_value: Any
) -> Generator[None, None, None]:
    """
    Context manager to temporarily modify a class attribute.

    Args:
        cls: The class to modify
        attribute_name: Name of the attribute to modify
        new_value: The temporary value to set

    Usage:
        with temporary_class_attribute(APIView, 'authentication_classes', [TokenAuth]):
            # code that uses the modified attribute
            pass
        # attribute is automatically restored
    """
    original_value = getattr(cls, attribute_name, None)
    setattr(cls, attribute_name, new_value)
    try:
        yield
    finally:
        if original_value is not None:
            setattr(cls, attribute_name, original_value)
        # If there was no original value, remove the attribute
        elif hasattr(cls, attribute_name):
            delattr(cls, attribute_name)
