import os
import shutil
from typing import Any

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Populate locales"

    def handle(self, *args: Any, **options: Any) -> None:
        langs = {lang for lang, _ in settings.LANGUAGES}

        existed_langs: set[str] = set(
            os.listdir(settings.APP_LOCALE)  # pyright: ignore
        )

        new_langs = langs - existed_langs

        delete_langs = existed_langs - langs

        print(f"Delete langs: {delete_langs}")

        for lang in delete_langs:
            lang_path = os.path.join(settings.APP_LOCALE, lang)
            shutil.rmtree(lang_path)

        mms_args = [f"-l={lang.replace('-', '_')}" for lang in new_langs]

        call_command("makemessages", mms_args)
