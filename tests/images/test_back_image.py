"""taiga-back-openid: the plugin loads with the image's settings module."""

from conftest import BACK_IMAGE, cli

ENV = {
    "TAIGA_SECRET_KEY": "image-tests",
    "ENABLE_OPENID": "True",
    "OPENID_USER_URL": "https://idp.example.test/userinfo",
    "OPENID_TOKEN_URL": "https://idp.example.test/token",
    "OPENID_CLIENT_ID": "taiga",
    "OPENID_CLIENT_SECRET": "secret",
}


def manage(*args: str):
    env_args = [arg for key, value in ENV.items() for arg in ("-e", f"{key}={value}")]
    return cli("run", "--rm", "--entrypoint", "python", *env_args, BACK_IMAGE, "manage.py", *args, check=False)


def test_manage_check_with_openid():
    result = manage("check")
    assert result.returncode == 0, result.stderr


def test_plugin_installed_with_openid():
    result = manage(
        "shell", "-c", "from django.conf import settings; print('taiga_contrib_openid_auth' in settings.INSTALLED_APPS)"
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "True"
