import shutil
from collections.abc import Generator

from django.conf import settings

import pytest
from _pytest.capture import CaptureFixture
from _pytest.main import Session


def pytest_sessionfinish(session: Session, exitstatus: int) -> None:
    if exitstatus != 0:
        return

    shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)


@pytest.fixture()
def no_warnings(
    capsys: CaptureFixture[str],
) -> Generator[CaptureFixture[str], None, None]:
    """make sure test emits no warnings"""
    yield capsys
    captured = capsys.readouterr()
    assert not captured.out
    assert not captured.err
