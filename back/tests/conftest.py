from unittest import mock

import pytest


def fake_response(status_code: int, json_data=None, content: bytes = b""):
    """A requests.Response stand-in; json_data=None makes .json() fail like an HTML page."""
    response = mock.Mock(status_code=status_code, content=content, text=content.decode())
    if json_data is None:
        response.json.side_effect = ValueError("not JSON")
    else:
        response.json.return_value = json_data
    return response


@pytest.fixture
def openid_settings(settings):
    """A configured plugin, defaults for everything optional."""
    settings.OPENID_CLIENT_ID = "taiga"
    settings.OPENID_CLIENT_SECRET = "secret"
    settings.OPENID_TOKEN_URL = "https://idp.example.test/token"
    settings.OPENID_USER_URL = "https://idp.example.test/userinfo"
    settings.OPENID_SCOPE = "openid email profile"
    for name in (
        "OPENID_FILTER",
        "OPENID_FILTER_FIELD",
        "OPENID_ID_FIELD",
        "OPENID_USERNAME_FIELD",
        "OPENID_FULLNAME_FIELD",
        "OPENID_EMAIL_FIELD",
    ):
        if hasattr(settings, name):
            delattr(settings, name)
    return settings
