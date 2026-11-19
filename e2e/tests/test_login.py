"""OpenID Connect login through the real Taiga front and back, against Keycloak."""

import re

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
