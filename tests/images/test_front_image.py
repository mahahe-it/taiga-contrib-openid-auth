"""taiga-front-openid: the plugin is served and conf.json extends upstream's."""

import hashlib
import json
from pathlib import Path

import pytest
from conftest import CONF, cli

PLUGIN_ENTRY = "plugins/openid-auth/openid-auth.json"
ENABLED = {
    "TAIGA_URL": "http://taiga.example.test",
    "ENABLE_OPENID": "true",
    "OPENID_URL": "https://idp.example.test/auth",
    "OPENID_CLIENT_ID": "taiga",
    "OPENID_NAME": "Example IdP",
}


def conf(container) -> dict:
    return json.loads(container.read(CONF))


def test_enabled_adds_plugin_and_keys(start_front):
    loaded = conf(start_front(ENABLED))
    assert loaded["contribPlugins"].count(PLUGIN_ENTRY) == 1
    assert loaded["openidAuth"] == "https://idp.example.test/auth"
    assert loaded["openidClientId"] == "taiga"
    assert loaded["openidName"] == "Example IdP"
    assert loaded["openidScope"] == "openid email"
    assert loaded["baseHref"] == "/"  # only upstream's 6.10 template has it


def test_disabled_leaves_upstream_conf(start_front):
    loaded = conf(start_front({**ENABLED, "ENABLE_OPENID": "false"}))
    assert PLUGIN_ENTRY not in loaded["contribPlugins"]
    assert "openidAuth" not in loaded


def test_restart_does_not_duplicate(start_front):
    container = start_front(ENABLED)
    container.restart()
    container.wait_http()
    assert conf(container)["contribPlugins"].count(PLUGIN_ENTRY) == 1


def test_mounted_conf_untouched(start_front, tmp_path):
    mounted = tmp_path / "conf.json"
    mounted.write_text('{"api": "http://mine.example.test/api/v1/", "contribPlugins": []}\n')
    mounted.chmod(0o644)
    container = start_front(ENABLED, volumes=(f"{mounted}:{CONF}:ro,z",))
    assert container.read(CONF) == mounted.read_text()


def test_plugin_files_served(start_front):
    container = start_front(ENABLED)
    plugin = json.loads(container.exec("wget", "-qO-", f"http://127.0.0.1/{PLUGIN_ENTRY}").stdout)
    assert plugin["module"] == "taigaContrib.openidAuth"
    js = container.exec("wget", "-qO-", "http://127.0.0.1/plugins/openid-auth/openid-auth.js").stdout
    assert "taigaContrib.openidAuth" in js


@pytest.mark.parametrize("missing", ["OPENID_URL", "OPENID_CLIENT_ID"])
def test_enabled_without_required_setting_warns(start_front, missing):
    container = start_front({key: value for key, value in ENABLED.items() if key != missing})
    assert f"openid-auth: warning: ENABLE_OPENID=true but {missing} is empty" in container.logs()


def test_failed_config_keeps_marker(start_front, tmp_path):
    """If extending conf.json fails, the next start must try again."""
    # Upstream's template writes DEBUG unquoted: this makes conf.json invalid JSON.
    container = start_front({**ENABLED, "DEBUG": "oops"}, wait=False)
    assert container.wait_exit() != 0
    result = cli("cp", f"{container.name}:/tmp/openid-conf-generated", str(tmp_path / "marker"), check=False)
    assert result.returncode == 0, result.stderr


def test_plugin_image_is_intact(start_front):
    """The build copies the button image byte for byte (gulp 5 reads files as text by default)."""
    container = start_front(ENABLED)
    served = container.exec("sha256sum", "/usr/share/nginx/html/plugins/openid-auth/images/openid.png").stdout.split()[0]
    source = Path(__file__).parents[2] / "front" / "images" / "openid.png"
    assert served == hashlib.sha256(source.read_bytes()).hexdigest()
