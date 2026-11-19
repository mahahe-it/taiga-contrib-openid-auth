# Settings of the taiga-back-openid image: upstream's env-driven config plus the
# OpenID Connect plugin. Selected with DJANGO_SETTINGS_MODULE=settings.openid, so a
# config.py mounted over upstream's keeps working.
import os

from .config import *
from .config import INSTALLED_APPS

ENABLE_OPENID = os.getenv("ENABLE_OPENID", "False") == "True"

if ENABLE_OPENID:
    # A mounted config.py may already add it (the old images appended it there)
    if "taiga_contrib_openid_auth" not in INSTALLED_APPS:
        INSTALLED_APPS += ["taiga_contrib_openid_auth"]

    # Only variables that are set and not empty: the plugin's defaults apply
    # to the others (Helm charts often render unset values as "").
    for _name in (
        "OPENID_USER_URL",
        "OPENID_TOKEN_URL",
        "OPENID_CLIENT_ID",
        "OPENID_CLIENT_SECRET",
        "OPENID_SCOPE",
        "OPENID_FILTER",
        "OPENID_FILTER_FIELD",
        "OPENID_ID_FIELD",
        "OPENID_USERNAME_FIELD",
        "OPENID_FULLNAME_FIELD",
        "OPENID_EMAIL_FIELD",
        "OPENID_TIMEOUT",
        "OPENID_TOKEN_AUTH_METHOD",
    ):
        if os.environ.get(_name, "").strip():
            globals()[_name] = os.environ[_name]

    for _name in (
        "OPENID_REQUIRE_VERIFIED_EMAIL",
        "OPENID_ALLOW_ACCESS_TOKEN",
        "OPENID_REGISTER_ENABLED",
    ):
        if os.environ.get(_name, "").strip():
            globals()[_name] = os.environ[_name].strip().lower() in ("true", "1", "yes")
