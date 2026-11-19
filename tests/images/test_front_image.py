"""taiga-front-openid: the plugin is served and conf.json extends upstream's."""

import json

from conftest import CONF

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
