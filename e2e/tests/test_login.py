"""OpenID Connect login through the real Taiga front and back, against Keycloak."""

import re
from urllib.parse import parse_qs, urlparse

import pytest
import requests
from conftest import (
    API_URL,
    OPENID_NAME,
    TAIGA_URL,
    admin_token,
    api_me,
    db_query,
    openid_login,
    stored_token,
    wait_for_token,
)
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


def register_local(username: str, email: str) -> int:
    """A password account, created through Taiga's public registration."""
    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "type": "public",
            "username": username,
            "email": email,
            "full_name": username,
            "password": f"{username}-pw",
            "accepted_terms": True,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["id"]


def test_existing_email_is_linked(page: Page):
    local_id = register_local("carol-local", "carol@example.test")

    openid_login(page, "carol")
    me = api_me(wait_for_token(page))
    assert me["id"] == local_id
    assert me["username"] == "carol-local"


def test_unverified_email_not_linked(page: Page):
    """Account takeover: an unverified email must not reach the existing account."""
    register_local("dave-local", "dave@example.test")

    openid_login(page, "dave")
    expect(page.get_by_text(re.compile("OPENID_REQUIRE_VERIFIED_EMAIL"))).to_be_visible(timeout=30_000)
    assert stored_token(page) is None


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


def test_access_token_login_disabled_by_default(page: Page):
    """A token from the URL is not Taiga's to trust: any client's token would do, and no state."""
    page.goto(f"{TAIGA_URL}/login?access_token=someone-elses-token")
    expect(page.get_by_text(re.compile("OPENID_ALLOW_ACCESS_TOKEN"))).to_be_visible(timeout=30_000)
    assert stored_token(page) is None


def test_invited_user_joins_project(page: Page):
    """Sign up with OpenID from an invitation: the membership is the new user's."""
    admin = {"Authorization": f"Bearer {admin_token()}"}
    # Taiga only lets a verified user invite; the superuser from manage.py is not.
    db_query("UPDATE users_user SET verified_email = true WHERE username = 'admin'")
    project = requests.post(
        f"{API_URL}/projects", json={"name": "Invitation E2E", "description": "e2e"}, headers=admin, timeout=30
    )
    project.raise_for_status()
    project_id = project.json()["id"]
    role_id = requests.get(f"{API_URL}/roles", params={"project": project_id}, headers=admin, timeout=10).json()[0]["id"]
    invite = requests.post(
        f"{API_URL}/memberships/bulk_create",
        json={"project_id": project_id, "bulk_memberships": [{"role_id": role_id, "username": "erin@example.test"}]},
        headers=admin,
        timeout=30,
    )
    invite.raise_for_status()
    [(invitation,)] = db_query(
        "SELECT token FROM projects_membership WHERE project_id = %s AND email = %s", project_id, "erin@example.test"
    )

    openid_login(page, "erin", path=f"/invitation/{invitation}")
    token = wait_for_token(page)
    erin = api_me(token)
    assert erin["username"] == "erin"
    member_of = requests.get(
        f"{API_URL}/projects", params={"member": erin["id"]}, headers={"Authorization": f"Bearer {token}"}, timeout=10
    ).json()
    assert project_id in [p["id"] for p in member_of]
