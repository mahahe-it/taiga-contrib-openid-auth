"""Helpers for the e2e tests: Taiga at TAIGA_URL, Keycloak realm `taiga`."""

import json
import os
import re

import psycopg
import pytest
import requests
from playwright.sync_api import Browser, Page

TAIGA_URL = os.environ.get("TAIGA_URL", "http://taiga-gateway")
API_URL = f"{TAIGA_URL}/api/v1"
KEYCLOAK_PASSWORD = "e2e"
OPENID_NAME = "Keycloak E2E"


def openid_login(page: Page, username: str, path: str = "/login") -> None:
    """Click the OpenID button on a Taiga page (login by default) and sign in on Keycloak."""
    page.goto(f"{TAIGA_URL}{path}")
    page.get_by_text(f"Sign in with {OPENID_NAME}").click()
    page.wait_for_url(re.compile(r"^http://keycloak:8080/"))
    page.fill("#username", username)
    page.fill("#password", KEYCLOAK_PASSWORD)
    page.click("#kc-login")


def stored_token(page: Page) -> str | None:
    raw = page.evaluate("() => window.localStorage.getItem('token')")
    return json.loads(raw) if raw else None


def wait_for_token(page: Page) -> str:
    page.wait_for_function("() => window.localStorage.getItem('token')", timeout=30_000)
    token = stored_token(page)
    assert token
    return token


def admin_token() -> str:
    response = requests.post(
        f"{API_URL}/auth", json={"type": "normal", "username": "admin", "password": "e2e-admin"}, timeout=10
    )
    response.raise_for_status()
    return response.json()["auth_token"]


def db_query(sql: str, *params):
    """Taiga's database, for what the API does not expose (invitation tokens)."""
    with psycopg.connect("host=taiga-db dbname=taiga user=taiga password=taiga") as conn:
        cursor = conn.execute(sql, params)
        return cursor.fetchall() if cursor.description else []


def api_me(token: str) -> dict:
    response = requests.get(
        f"{API_URL}/users/me", headers={"Authorization": f"Bearer {token}"}, timeout=10
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def new_page(browser: Browser):
    """Pages in fresh contexts: no Taiga token, no Keycloak session."""
    contexts = []

    def make() -> Page:
        context = browser.new_context()
        contexts.append(context)
        return context.new_page()

    yield make
    for context in contexts:
        context.close()
