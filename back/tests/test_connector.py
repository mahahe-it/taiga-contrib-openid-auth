"""connector.py: token/userinfo calls, field mapping and the group filter (HTTP mocked)."""

import json
from unittest import mock

import pytest
from conftest import fake_response
from taiga.base.api.renderers import UnicodeJSONRenderer
from taiga.base.exceptions import AuthenticationFailed, format_exception
from taiga_contrib_openid_auth import connector

USERINFO = {
    "sub": "abc-123",
    "preferred_username": "alice",
    "name": "Alice E2E",
    "email": "alice@example.test",
    "groups": ["taiga_users"],
}


def profile(data, status_code=200):
    with mock.patch("requests.get", return_value=fake_response(status_code, data)):
        return connector.get_user_profile(headers={})


def test_login_requires_client_config(openid_settings):
    openid_settings.OPENID_CLIENT_ID = None
    with pytest.raises(connector.OpenIDApiError):
        connector.login("code", None, "http://taiga/login")


def test_login_posts_code_to_token_url(openid_settings):
    reply = fake_response(200, {"access_token": "tok"})
    with mock.patch("requests.post", return_value=reply) as post:
        auth = connector.login("the-code", None, "http://taiga/login")
    assert auth.access_token == "tok"
    url = post.call_args.args[0]
    data = post.call_args.kwargs["data"]
    assert url == "https://idp.example.test/token"
    assert data["grant_type"] == "authorization_code"
    assert data["code"] == "the-code"
    assert data["redirect_uri"] == "http://taiga/login"
    assert data["scope"] == "openid email profile"


def test_login_with_access_token_skips_token_call(openid_settings):
    with mock.patch("requests.post") as post:
        auth = connector.login(None, "given-token", "http://taiga/login")
    assert auth.access_token == "given-token"
    post.assert_not_called()


def test_filter_allows_user_in_group(openid_settings):
    openid_settings.OPENID_FILTER = "taiga_users"
    openid_settings.OPENID_FILTER_FIELD = "groups"
    assert profile(USERINFO).username == "alice"


def test_filter_rejects_user_outside_group(openid_settings):
    openid_settings.OPENID_FILTER = "taiga_admins"
    openid_settings.OPENID_FILTER_FIELD = "groups"
    with pytest.raises(AuthenticationFailed):
        profile(USERINFO)


def test_filter_missing_claim_rejects(openid_settings):
    openid_settings.OPENID_FILTER = "taiga_users"
    openid_settings.OPENID_FILTER_FIELD = "roles"
    with pytest.raises(AuthenticationFailed):
        profile(USERINFO)


def test_filter_values_are_trimmed(openid_settings):
    openid_settings.OPENID_FILTER = "taiga_users, taiga_admins"
    openid_settings.OPENID_FILTER_FIELD = "groups"
    assert profile({**USERINFO, "groups": ["taiga_admins"]}).username == "alice"


def test_filter_claim_as_string(openid_settings):
    openid_settings.OPENID_FILTER = "taiga_users"
    openid_settings.OPENID_FILTER_FIELD = "groups"
    assert profile({**USERINFO, "groups": "taiga_users"}).username == "alice"
    with pytest.raises(AuthenticationFailed):
        profile({**USERINFO, "groups": "t"})


def test_username_fallback_order(openid_settings):
    data = {"sub": "1", "username": "from-username", "email": "e@example.test"}
    assert profile(data).username == "from-username"
    assert profile({"sub": "1", "email": "e@example.test"}).username == "e@example.test"


def test_field_mapping_from_settings(openid_settings):
    openid_settings.OPENID_ID_FIELD = "oid"
    openid_settings.OPENID_USERNAME_FIELD = "nickname"
    openid_settings.OPENID_FULLNAME_FIELD = "display_name"
    openid_settings.OPENID_EMAIL_FIELD = "mail"
    user = profile(
        {"oid": "o-1", "nickname": "ali", "display_name": "Alice D", "mail": "a@example.test"}
    )
    assert user == connector.User(id="o-1", username="ali", full_name="Alice D", email="a@example.test")


def test_userinfo_non_json_error(openid_settings):
    with pytest.raises(connector.OpenIDApiError) as excinfo:
        profile(None, status_code=401)
    assert excinfo.value.detail["status_code"] == 401


def test_token_error_in_body(openid_settings):
    reply = fake_response(200, {"error": "invalid_grant"})
    with mock.patch("requests.post", return_value=reply), pytest.raises(connector.OpenIDApiError) as excinfo:
        connector.login("code", None, "http://taiga/login")
    assert excinfo.value.detail["error"] == "invalid_grant"


def test_default_scope_is_openid_email(openid_settings):
    del openid_settings.OPENID_SCOPE
    reply = fake_response(200, {"access_token": "tok"})
    with mock.patch("requests.post", return_value=reply) as post:
        connector.login("the-code", None, "http://taiga/login")
    assert post.call_args.kwargs["data"]["scope"] == "openid email"


def rendered(exc) -> dict:
    """The body Taiga's exception handler would send for this exception."""
    return json.loads(UnicodeJSONRenderer().render(format_exception(exc)))


def test_token_non_json_error_renders(openid_settings):
    reply = fake_response(405, None, content=b"<html>Method Not Allowed</html>")
    with mock.patch("requests.post", return_value=reply), pytest.raises(connector.OpenIDApiError) as excinfo:
        connector.login("code", None, "http://taiga/login")
    assert rendered(excinfo.value)["status_code"] == 405


def test_token_error_renders(openid_settings):
    reply = fake_response(401, {"error": "unauthorized_client"}, content=b'{"error": "unauthorized_client"}')
    with mock.patch("requests.post", return_value=reply), pytest.raises(connector.OpenIDApiError) as excinfo:
        connector.login("code", None, "http://taiga/login")
    body = rendered(excinfo.value)
    assert body["status_code"] == 401
    assert body["error"] == "unauthorized_client"
