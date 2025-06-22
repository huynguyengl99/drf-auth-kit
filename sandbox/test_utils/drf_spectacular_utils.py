import difflib
import json
import os
from collections.abc import Callable
from typing import Any

from drf_spectacular.validation import (
    validate_schema,
)


def build_absolute_file_path(relative_path: str) -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), relative_path
    )


def assert_schema(
    schema: dict[str, Any],
    reference_filename: str,
    transforms: list[Callable[[str], str]] | None = None,
    reverse_transforms: list[Callable[[str], str]] | None = None,
) -> None:
    from drf_spectacular.renderers import OpenApiJsonRenderer, OpenApiYamlRenderer

    schema_yml = OpenApiYamlRenderer().render(schema, renderer_context={})  # type: ignore
    # render also a json and provoke serialization issues
    OpenApiJsonRenderer().render(schema, renderer_context={})

    reference_filename = build_absolute_file_path(reference_filename)

    with open(reference_filename.replace(".yml", "_out.yml"), "wb") as fh:
        fh.write(schema_yml)  # pyright: ignore[reportUnknownArgumentType]

    if not os.path.exists(reference_filename):
        raise RuntimeError(
            f"{reference_filename} was not found for comparison. Carefully inspect "
            f'the generated {reference_filename.replace(".yml", "_out.yml")} and '
            f"copy it to {reference_filename} to serve as new ground truth."
        )

    generated = schema_yml.decode()

    with open(reference_filename) as fh:
        expected = fh.read()

    # apply optional transformations to generated result. this mainly serves to unify
    # discrepancies between Django, DRF and library versions.
    for t in transforms or []:
        generated = t(generated)
    for t in reverse_transforms or []:
        expected = t(expected)

    assert_equal(generated, expected)
    # this is more a less a sanity check as checked-in schemas should be valid anyhow
    validate_schema(schema)  # type: ignore


def assert_equal(actual: str | dict[str, Any], expected: str | dict[str, Any]) -> None:
    if not isinstance(actual, str):
        actual = json.dumps(actual, indent=4)
    if not isinstance(expected, str):
        expected = json.dumps(expected, indent=4)
    diff = difflib.unified_diff(
        expected.splitlines(True),
        actual.splitlines(True),
    )
    diff = "".join(diff)  # type: ignore[assignment]
    assert actual == expected and not diff, diff


def generate_schema(
    route: str | None,
    viewset: type | None = None,
    view: type | None = None,
    view_function: Callable[..., Any] | None = None,
    patterns: list[Any] | None = None,
) -> dict[str, Any]:
    from django.urls import path
    from rest_framework import routers
    from rest_framework.viewsets import ViewSetMixin

    from drf_spectacular.generators import SchemaGenerator

    if viewset:
        assert issubclass(viewset, ViewSetMixin)
        router = routers.SimpleRouter()
        router.register(route, viewset, basename=route)  # type: ignore
        patterns = router.urls
    elif view:
        patterns = [path(route, view.as_view())]  # type: ignore
    elif view_function:
        patterns = [path(route, view_function)]  # type: ignore
    else:
        assert route is None and isinstance(patterns, list)

    generator = SchemaGenerator(patterns=patterns)  # type: ignore
    schema = generator.get_schema(request=None, public=True)  # type: ignore
    validate_schema(schema)  # type: ignore
    return schema  # type: ignore


def get_response_schema(
    operation: dict[str, Any],
    status: str | None = None,
    content_type: str = "application/json",
) -> dict[str, Any]:
    if (
        not status
        and operation["operationId"].endswith("_create")
        and "201" in operation["responses"]
        and "200" not in operation["responses"]
    ):
        status = "201"
    elif not status:
        status = "200"
    return operation["responses"][status]["content"][content_type]["schema"]  # type: ignore


def get_request_schema(
    operation: dict[str, Any], content_type: str = "application/json"
) -> dict[str, Any]:
    return operation["requestBody"]["content"][content_type]["schema"]  # type: ignore


def is_gis_installed() -> bool:
    # only load GIS if library is installed. This is required for the GIS test to work
    from django.core.exceptions import ImproperlyConfigured

    try:
        from django.contrib.gis.gdal import (
            gdal_version,  # noqa: F401 # pyright: ignore[reportUnusedImport]
        )
    except ImproperlyConfigured:
        return False
    else:
        return True


def strip_int64_details(schema: dict[str, Any]) -> dict[str, Any]:
    """remove new min/max/format for django 5 with sqlite db for comparison's sake"""

    if schema.get("format") == "int64" and "minimum" in schema and "maximum" in schema:
        return {
            k: v for k, v in schema.items() if k not in ("format", "minimum", "maximum")
        }
    else:
        return schema
