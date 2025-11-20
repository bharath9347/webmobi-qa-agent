"""
Pytest automation that validates the Create Event workflow on events.webmobi.com.

Setup
-----
1. Create a `.env` file in the project root with:

   WEBMOBI_EMAIL="<your email>"
   WEBMOBI_PASSWORD="<your password>"

2. Install dependencies:

   pip install pytest playwright python-dotenv
   playwright install
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, Playwright, expect, sync_playwright

# Load secrets from the local .env file so that credentials never live in code.
load_dotenv()

BASE_URL = "https://events.webmobi.com"
LOGIN_URL = f"{BASE_URL}/login"
SCREENSHOT_DIR = Path("test-results")
SCREENSHOT_DIR.mkdir(exist_ok=True)


def _screenshot_path(prefix: str, success: bool) -> Path:
    """Generate a descriptive screenshot path to capture success/failure context."""
    status = "success" if success else "failure"
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    filename = f"{prefix}-{status}-{timestamp}.png"
    return SCREENSHOT_DIR / filename


@pytest.fixture(scope="session")
def credentials() -> dict[str, str]:
    """Return the login credentials sourced from environment variables."""
    email = os.getenv("WEBMOBI_EMAIL")
    password = os.getenv("WEBMOBI_PASSWORD")
    if not email or not password:
        raise RuntimeError(
            "Missing WEBMOBI_EMAIL or WEBMOBI_PASSWORD in the .env file. "
            "Create a .env file with both variables before running the test."
        )
    return {"email": email, "password": password}


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """Share a Playwright instance across tests to reduce startup overhead."""
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture
def page(playwright_instance: Playwright) -> Generator[Page, None, None]:
    """Provide a fresh browser context for every test to keep state isolated."""
    browser = playwright_instance.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    try:
        yield page
    finally:
        context.close()
        browser.close()


@pytest.mark.e2e
def test_create_event(page: Page, credentials: dict[str, str]) -> None:
    """E2E test: login, create an event, and verify the creation succeeded."""
    event_suffix = uuid.uuid4().hex[:6]
    event_name = f"Automation Event {datetime.utcnow():%Y%m%d%H%M%S}-{event_suffix}"
    screenshot_prefix = event_name.replace(" ", "-").lower()

    try:
        # Navigate directly to the login page and wait for all resources to settle.
        page.goto(LOGIN_URL, wait_until="networkidle")

        # Populate the email + password inputs using accessible name / placeholder selectors.
        page.fill("input[name='email'], input#email", credentials["email"])
        page.fill("input[name='password'], input#password", credentials["password"])

        # Submit the login form and block until the dashboard content is ready.
        page.click("button:has-text('Login'), button[type='submit']")
        page.wait_for_url("**/dashboard**", timeout=60_000)
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        # Start the Create Event flow from the dashboard.
        page.get_by_role("button", name="Create Event").click()
        page.wait_for_selector("form#create-event-form, form:has-text('Create Event')", timeout=30_000)

        # Fill out the minimum required fields using the unique event name.
        page.fill("input[name='eventName'], input#eventName", event_name)
        page.fill("textarea[name='eventDescription'], textarea#eventDescription", "QA automation smoke event.")
        page.fill("input[name='eventStartDate'], input#eventStartDate", datetime.utcnow().strftime("%Y-%m-%d"))

        # Submit the form and wait for a visual confirmation or list row update.
        page.get_by_role("button", name="Create").click()

        # Validation Strategy: either a toast appears or the new event shows up in the list.
        success_toast = page.get_by_text("Event created successfully", exact=False)
        event_in_list = page.get_by_role("link", name=event_name)
        expect(success_toast.or_(event_in_list)).to_be_visible(timeout=60_000)

        # Capture a success screenshot for traceability.
        page.screenshot(path=_screenshot_path(screenshot_prefix, success=True), full_page=True)

    except Exception as exc:
        # Save state before propagating the exception for easier debugging in CI.
        page.screenshot(path=_screenshot_path(screenshot_prefix, success=False), full_page=True)
        raise AssertionError(f"Create Event flow failed: {exc}") from exc

