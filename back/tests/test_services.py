"""services.py: linking an OpenID identity to an existing account by email."""

import pytest
from taiga.base.exceptions import AuthenticationFailed
from taiga_contrib_openid_auth import services


def test_verified_email_links(openid_settings):
    services.check_email_link(True)


def test_unverified_email_refused_by_default(openid_settings):
    with pytest.raises(AuthenticationFailed, match="OPENID_REQUIRE_VERIFIED_EMAIL"):
        services.check_email_link(False)


@pytest.mark.parametrize("value", [False, "False", "false"])
def test_unverified_email_links_when_not_required(openid_settings, value):
    openid_settings.OPENID_REQUIRE_VERIFIED_EMAIL = value
    services.check_email_link(False)


@pytest.mark.parametrize("value", [True, "True"])
def test_unverified_email_refused_when_required(openid_settings, value):
    openid_settings.OPENID_REQUIRE_VERIFIED_EMAIL = value
    with pytest.raises(AuthenticationFailed):
        services.check_email_link(False)


@pytest.mark.parametrize("unset", [None, ""])
def test_unset_require_verified_email_keeps_default(openid_settings, unset):
    openid_settings.OPENID_REQUIRE_VERIFIED_EMAIL = unset
    with pytest.raises(AuthenticationFailed):
        services.check_email_link(False)


@pytest.mark.parametrize("public", [True, False])
@pytest.mark.parametrize("unset", ["absent", None, ""])
def test_register_follows_public_register_by_default(openid_settings, public, unset):
    openid_settings.PUBLIC_REGISTER_ENABLED = public
    if unset != "absent":
        openid_settings.OPENID_REGISTER_ENABLED = unset
    assert services.register_enabled() is public


@pytest.mark.parametrize(("value", "expected"), [(True, True), ("True", True), (False, False), ("false", False)])
@pytest.mark.parametrize("public", [True, False])
def test_register_setting_overrides_public_register(openid_settings, public, value, expected):
    openid_settings.PUBLIC_REGISTER_ENABLED = public
    openid_settings.OPENID_REGISTER_ENABLED = value
    assert services.register_enabled() is expected
