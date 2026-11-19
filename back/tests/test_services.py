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
