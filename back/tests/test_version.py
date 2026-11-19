"""__version__: from the installed distribution, or a placeholder from a source checkout."""

import importlib
from importlib.metadata import PackageNotFoundError
from unittest import mock

import taiga_contrib_openid_auth


def test_version_of_installed_package():
    assert taiga_contrib_openid_auth.__version__ != "0.0.0"


def test_version_from_source_checkout():
    with mock.patch("importlib.metadata.version", side_effect=PackageNotFoundError("taiga-contrib-openid-auth")):
        reloaded = importlib.reload(taiga_contrib_openid_auth)
    try:
        assert reloaded.__version__ == "0.0.0"
    finally:
        importlib.reload(taiga_contrib_openid_auth)
