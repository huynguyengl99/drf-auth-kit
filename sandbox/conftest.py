import shutil

from django.conf import settings

from _pytest.main import Session


def pytest_sessionfinish(session: Session, exitstatus: int) -> None:
    if exitstatus != 0:
        return

    shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
