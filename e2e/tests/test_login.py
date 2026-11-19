"""OpenID Connect login through the real Taiga front and back, against Keycloak."""

import re
from urllib.parse import parse_qs, urlparse

import pytest
import requests
from conftest import API_URL, OPENID_NAME, TAIGA_URL, api_me, openid_login, stored_token, wait_for_token
from playwright.sync_api import Page, expect


def test_password_login_admin(page: Page):
    """Harness sanity: the stack works without the plugin being involved."""
    page.goto(f"{TAIGA_URL}/login")
    page.fill("input[name='username']", "admin")
    page.fill("input[name='password']", "e2e-admin")
    page.click("button[type='submit']")
    assert api_me(wait_for_token(page))["username"] == "admin"


def test_openid_button_shown(page: Page):
    page.goto(f"{TAIGA_URL}/login")
    expect(page.get_by_text(f"Sign in with {OPENID_NAME}")).to_be_visible()


def test_signup_then_relogin_same_user(new_page):
    first = new_page()
    openid_login(first, "alice")
    me = api_me(wait_for_token(first))
    assert me["username"] == "alice"
    assert me["email"] == "alice@example.test"
    assert me["full_name"] == "Alice E2E"

    second = new_page()
    openid_login(second, "alice")
    assert api_me(wait_for_token(second))["id"] == me["id"]


def test_user_outside_filter_rejected(page: Page):
    openid_login(page, "bob")
    expect(page.get_by_text(re.compile("OPENID_FILTER"))).to_be_visible(timeout=30_000)
    assert stored_token(page) is None


def test_existing_email_is_linked(page: Page):
    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "type": "public",
            "username": "carol-local",
            "email": "carol@example.test",
            "full_name": "Carol Local",
            "password": "carol-local-pw",
            "accepted_terms": True,
        },
        timeout=10,
    )
    response.raise_for_status()
    local_id = response.json()["id"]

    openid_login(page, "carol")
    me = api_me(wait_for_token(page))
    assert me["id"] == local_id
    assert me["username"] == "carol-local"


def held_callback(page: Page) -> dict[str, str]:
    """Sign in as alice on Keycloak and return the callback's query, code unused.

    Keycloak's redirect back to Taiga is answered with an empty page, so the
    front never redeems the code: it stays valid for the forged callbacks.
    Playwright does not route redirects, so the form post is intercepted.
    """
    captured = []

    def hold(route):
        response = route.fetch(max_redirects=0)
        location = response.headers.get("location", "")
        if location.startswith(f"{TAIGA_URL}/login?") and "code=" in location:
            captured.append(location)
            route.fulfill(status=200, content_type="text/html", body="<html></html>")
        else:
            route.fulfill(response=response)

    page.route(re.compile(r"^http://keycloak:8080/realms/taiga/login-actions/"), hold)
    openid_login(page, "alice")
    page.wait_for_url(re.compile(r"/login-actions/"))
    page.wait_for_load_state()
    assert captured, "Keycloak did not redirect back to Taiga"
    return {key: values[0] for key, values in parse_qs(urlparse(captured[0]).query).items()}


def test_callback_carries_state(new_page):
    assert held_callback(new_page())["state"].startswith("openid-")


@pytest.mark.parametrize("state", [None, "openid-forged"], ids=["missing", "forged"])
def test_callback_without_matching_state_rejected(new_page, state):
    """Login CSRF: a code obtained by someone else must not sign the victim in."""
    code = held_callback(new_page())["code"]

    victim = new_page()
    query = f"code={code}" + (f"&state={state}" if state else "")
    victim.goto(f"{TAIGA_URL}/login?{query}")
    expect(victim.get_by_text(re.compile("does not match this login attempt"))).to_be_visible(timeout=30_000)
    assert stored_token(victim) is None
