"""settings/openid.py: the image's env contract (DJANGO_SETTINGS_MODULE=settings.openid)."""

import json
import os
import shutil
import subprocess
import sys

import pytest

ALL_VARS = {
    "OPENID_USER_URL": "https://idp.example.test/userinfo",
    "OPENID_TOKEN_URL": "https://idp.example.test/token",
    "OPENID_CLIENT_ID": "taiga",
    "OPENID_CLIENT_SECRET": "secret",
    "OPENID_SCOPE": "openid email profile",
    "OPENID_FILTER": "taiga_users",
    "OPENID_FILTER_FIELD": "groups",
    "OPENID_ID_FIELD": "oid",
    "OPENID_USERNAME_FIELD": "nickname",
    "OPENID_FULLNAME_FIELD": "display_name",
    "OPENID_EMAIL_FIELD": "mail",
    "OPENID_TIMEOUT": "5",
}

BOOL_VARS = ["OPENID_REQUIRE_VERIFIED_EMAIL", "OPENID_ALLOW_ACCESS_TOKEN"]

PROBE = """
import json, django
from django.conf import settings
django.setup()
names = NAMES
print(json.dumps({
    "installed": "taiga_contrib_openid_auth" in settings.INSTALLED_APPS,
    "values": {n: getattr(settings, n, None) for n in names},
    "defined": {n: hasattr(settings, n) for n in names},
}))
""".replace("NAMES", repr(sorted([*ALL_VARS, *BOOL_VARS])))


def load_settings(env: dict, cwd: str = "/taiga-back") -> dict:
    clean = {k: v for k, v in os.environ.items() if not k.startswith(("OPENID_", "ENABLE_OPENID"))}
    clean["DJANGO_SETTINGS_MODULE"] = "settings.openid"
    clean["PYTHONPATH"] = "/taiga-back"
    result = subprocess.run(
        [sys.executable, "-c", PROBE],
        env={**clean, **env},
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_openid_settings_from_env():
    loaded = load_settings({"ENABLE_OPENID": "True", **ALL_VARS})
    assert loaded["installed"] is True
    assert {name: loaded["values"][name] for name in ALL_VARS} == ALL_VARS


@pytest.mark.parametrize("name", BOOL_VARS)
@pytest.mark.parametrize(("env", "value"), [("True", True), ("true", True), ("False", False), ("no", False)])
def test_bool_setting_from_env(name, env, value):
    loaded = load_settings({"ENABLE_OPENID": "True", name: env})
    assert loaded["values"][name] is value


@pytest.mark.parametrize("name", BOOL_VARS)
def test_bool_setting_unset_keeps_connector_default(name):
    loaded = load_settings({"ENABLE_OPENID": "True"})
    assert loaded["defined"][name] is False


def test_unset_field_env_keeps_connector_default():
    loaded = load_settings({"ENABLE_OPENID": "True", "OPENID_CLIENT_ID": "taiga"})
    assert loaded["defined"]["OPENID_USERNAME_FIELD"] is False
    assert loaded["defined"]["OPENID_SCOPE"] is False


def test_disabled_does_not_install_app():
    loaded = load_settings({"ENABLE_OPENID": "False", **ALL_VARS})
    assert loaded["installed"] is False


def test_mounted_config_already_adding_the_app(tmp_path):
    """A config.py copied from the old images (snippet appended) is mounted over upstream's."""
    shutil.copytree("/taiga-back/settings", tmp_path / "settings")
    with open(tmp_path / "settings" / "config.py", "a") as config:
        config.write('\nINSTALLED_APPS += ["taiga_contrib_openid_auth"]\n')
    loaded = load_settings({"ENABLE_OPENID": "True", **ALL_VARS}, cwd=str(tmp_path))
    assert loaded["installed"] is True
