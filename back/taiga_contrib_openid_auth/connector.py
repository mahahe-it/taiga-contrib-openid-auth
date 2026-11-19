# Copyright (C) 2014-2017 Andrey Antukh <niwi@niwi.nz>
# Copyright (C) 2014-2017 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014-2017 David Barragán <bameda@dbarragan.com>
# Copyright (C) 2014-2017 Alejandro Alonso <alejandro.alonso@kaleidos.net>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from collections import namedtuple

import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from taiga.base.connectors.exceptions import ConnectorBaseException
from taiga.base.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class OpenIDApiError(ConnectorBaseException):
    pass


######################################################
# Data
######################################################

# Settings are read at call time (see _setting), these are their defaults.
DEFAULTS = {
    "OPENID_CLIENT_ID": None,
    "OPENID_CLIENT_SECRET": None,
    "OPENID_SCOPE": "openid email",
    "OPENID_TOKEN_URL": None,
    "OPENID_USER_URL": None,
    "OPENID_FILTER": "",
    "OPENID_FILTER_FIELD": None,
    "OPENID_ID_FIELD": "sub",
    "OPENID_USERNAME_FIELD": "preferred_username",
    "OPENID_FULLNAME_FIELD": "name",
    "OPENID_EMAIL_FIELD": "email",
    "OPENID_REQUIRE_VERIFIED_EMAIL": True,
    "OPENID_ALLOW_ACCESS_TOKEN": False,
    "OPENID_TIMEOUT": 10,
}

HEADERS = {"Accept": "application/json", }

AuthInfo = namedtuple("AuthInfo", ["access_token"])
User = namedtuple("User", ["id", "username", "full_name", "email", "email_verified"])

######################################################
# utils
######################################################


def _setting(name: str):
    """
    A setting, or its default when unset. None and "" count as unset: old-style
    config.py files set every variable with os.getenv, and Helm charts often
    render unset values as empty strings.
    """
    value = getattr(settings, name, None)
    if value is None or (isinstance(value, str) and not value.strip()):
        return DEFAULTS[name]
    return value


def is_true(value) -> bool:
    """A boolean claim or setting: some providers send "true" as a string, env vars are strings."""
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return value is True


def _json_or_none(response):
    try:
        return response.json()
    except ValueError:
        return None


def _request(method, url: str, **kwargs):
    """
    Call the provider within OPENID_TIMEOUT seconds: a provider that hangs or
    cannot be reached must not hold the worker until gunicorn kills it.
    """
    timeout = float(_setting("OPENID_TIMEOUT"))
    try:
        return method(url, timeout=timeout, **kwargs)
    except requests.Timeout:
        error = f"the identity provider did not answer within {timeout:g} s"
    except requests.RequestException as e:
        error = f"the identity provider could not be reached ({e.__class__.__name__})"
    logger.warning("OpenID: %s: %s", error, url)
    raise OpenIDApiError({"error": error, "url": url})


def _get(url: str, headers: dict) -> dict:
    """
    Make a GET call.
    """
    response = _request(requests.get, url, headers=headers)
    data = _json_or_none(response)
    if response.status_code != 200 or not isinstance(data, dict):
        error = data.get("error", "") if isinstance(data, dict) else "response is not JSON"
        raise OpenIDApiError({"status_code": response.status_code,
                              "error": error})
    return data


def _post(url: str, params: dict, headers: dict) -> dict:
    """
    Make a POST call.
    """
    response = _request(requests.post, url, data=params, headers=headers)
    data = _json_or_none(response)
    # The detail goes into Taiga's JSON error response: text only, never bytes.
    if not isinstance(data, dict):
        raise OpenIDApiError({"status_code": response.status_code,
                              "error": "error from data not retrievable",
                              "content": response.text[:500]})
    if response.status_code != 200 or "error" in data:
        raise OpenIDApiError({"status_code": response.status_code,
                              "error": data.get("error", ""),
                              "content": response.text[:500]})
    return data


def _check_filter(data: dict) -> None:
    """
    Reject the user unless the OPENID_FILTER_FIELD claim holds one of the
    comma separated OPENID_FILTER values. The claim can be a list or a single string.
    """
    filter_field = _setting("OPENID_FILTER_FIELD")
    if not filter_field:
        return

    claim = data.get(filter_field, None)
    if claim is None:
        raise AuthenticationFailed(f"OPENID_FILTER_CLAIM provided but '{filter_field}' not found in UserInfo")

    if isinstance(claim, str):
        claim_values = {claim}
    elif isinstance(claim, list) and all(isinstance(value, str) for value in claim):
        claim_values = set(claim)
    else:
        raise AuthenticationFailed(
            f"OPENID_FILTER_FIELD '{filter_field}' must be a string or a list of strings, "
            f"not {type(claim).__name__}")
    allowed = {value.strip() for value in _setting("OPENID_FILTER").split(",") if value.strip()}
    if not allowed & claim_values:
        raise AuthenticationFailed("User does not satisfy OPENID_FILTER")


def _required_claim(data: dict, setting: str) -> str:
    """The userinfo claim named by `setting`, as a string; refuse the login without it."""
    claim = _setting(setting)
    value = data.get(claim, None)
    if value in (None, ""):
        raise AuthenticationFailed(
            f"The identity provider did not send the '{claim}' claim ({setting}). "
            "Check the scope (OPENID_SCOPE) and the claim mapping.")
    return str(value)


######################################################
# Simple calls
######################################################

def login(access_code: str, token: str, redirect_uri: str, headers: dict = HEADERS):
    """
    Get access_token fron an user authorized code, the client id and the client secret key.
    (See http://openid.net/specs/openid-connect-core-1_0.html#TokenEndpoint).
    """
    client_id = _setting("OPENID_CLIENT_ID")
    client_secret = _setting("OPENID_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise OpenIDApiError({"error_message": _(
            "The OpenID Connect plugin isn't properly configured. Please contact your sysadmin.")})

    if token:
        # Only the userinfo call checks the token, and it accepts a token issued
        # to any client of the provider: off unless a reverse proxy needs it.
        if not is_true(_setting("OPENID_ALLOW_ACCESS_TOKEN")):
            raise AuthenticationFailed(_(
                "Signing in with an access token is disabled (OPENID_ALLOW_ACCESS_TOKEN)."))
        return AuthInfo(access_token=token)

    params = {"grant_type": "authorization_code",
              "code": access_code,
              "client_id": client_id,
              "client_secret": client_secret,
              "redirect_uri": redirect_uri,
              "scope": _setting("OPENID_SCOPE"),
              }
    data = _post(_setting("OPENID_TOKEN_URL"), params=params, headers=headers)
    return AuthInfo(access_token=data.get("access_token", None))


def get_user_profile(headers: dict = HEADERS):
    """
    Get authenticated user info.
    (See openid.net/specs/openid-connect-core-1_0.html#UserInfo).
    """
    data = _get(_setting("OPENID_USER_URL"), headers=headers)
    _check_filter(data)

    user_id = _required_claim(data, "OPENID_ID_FIELD")
    email = _required_claim(data, "OPENID_EMAIL_FIELD")

    # Ends with the email, which is there: a username is always found.
    for field in (_setting("OPENID_USERNAME_FIELD"), "preferred_username", "full_name", "username", "email"):
        if data.get(field, None) not in (None, ""):
            username = str(data[field])
            break

    # Taiga needs a full name; providers send `name` only with the `profile` scope.
    full_name = data.get(_setting("OPENID_FULLNAME_FIELD"), None)
    full_name = str(full_name) if full_name not in (None, "") else username

    return User(id=user_id,
                username=username,
                full_name=full_name,
                email=email,
                email_verified=is_true(data.get("email_verified", None)),
                )

######################################################
# Convined calls
######################################################


def me(access_code: str, token: str, redirect_uri: str) -> tuple:
    """
    Connect to a openid account and get all personal info (profile and the primary email).
    """
    auth_info = login(access_code, token, redirect_uri)
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {auth_info.access_token}"
    user = get_user_profile(headers=headers)
    return user
