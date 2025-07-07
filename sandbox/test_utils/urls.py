from importlib import reload
from types import ModuleType


def reload_necessary_modules_and_get_urls() -> ModuleType:
    import auth_kit.utils

    reload(auth_kit.utils)

    import auth_kit.mfa.views.login

    reload(auth_kit.mfa.views.login)
    import auth_kit.mfa.views

    reload(auth_kit.mfa.views)
    import auth_kit.mfa.mfa_settings

    reload(auth_kit.mfa.mfa_settings)

    import auth_kit.utils

    reload(auth_kit.utils)
    import auth_kit.mfa.urls

    reload(auth_kit.mfa.urls)
    import auth_kit.urls

    reload(auth_kit.urls)

    return auth_kit.urls
