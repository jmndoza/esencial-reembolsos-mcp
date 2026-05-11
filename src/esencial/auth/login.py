"""Interactive login flow using real Chrome + CDP for session extraction.

Launches Chrome with remote debugging enabled. After the user completes
authentication (RUT, password, captcha, 2FA), connects via CDP to extract
cookies and the Auth0 access token from localStorage.
"""

import json
import subprocess
from concurrent.futures import ThreadPoolExecutor

from playwright.sync_api import sync_playwright

from esencial.auth.messages import (
    DIALOG_TITLE,
    ERR_EXTRACT_SESSION,
    ERR_NO_CREDENTIALS,
    LOGIN_PROMPT,
    SESSION_SAVED,
)
from esencial.auth.models import TokenData
from esencial.auth.session import save_session
from esencial.config import (
    CDP_PORT,
    CHROME_BIN,
    CHROME_PROFILE_DIR,
    DASHBOARD_URL,
    LOGIN_URL,
)

ESENCIAL_COOKIE_DOMAINS = [
    "https://sucursalvirtual.somosesencial.cl",
    "https://auth.somosesencial.cl",
    "https://www.somosesencial.cl",
]


def login() -> bool:
    """Run the full interactive login flow and persist the session.

    Opens Chrome at the Esencial login page, waits for the user to complete
    authentication, then extracts cookies and the Auth0 token via CDP and
    saves them to the Keychain.

    Returns:
        True on success, False if cancelled or credential extraction failed.
    """
    proc = _launch_chrome(LOGIN_URL)
    try:
        _show_dialog(LOGIN_PROMPT, wait_user=True)
        with ThreadPoolExecutor(max_workers=1) as ex:
            cookies, token_data = ex.submit(_extract_session_via_cdp).result()

        if not cookies or not (token_data and token_data.get("access_token")):
            _show_dialog(ERR_NO_CREDENTIALS)
            return False

        save_session(cookies, token_data=token_data)
        _show_dialog(SESSION_SAVED)
        return True

    except RuntimeError:
        return False
    except Exception as e:
        _show_dialog(ERR_EXTRACT_SESSION.format(error=e))
        return False
    finally:
        proc.terminate()


def _show_dialog(message: str, *, wait_user: bool = False) -> None:
    """Show a native macOS dialog via osascript.

    If wait_user is True and the user cancels, raises RuntimeError.
    """
    safe = message.replace("\\", "\\\\").replace('"', '\\"')
    result = subprocess.run(
        [
            "osascript", "-e",
            f'display dialog "{safe}" with title "{DIALOG_TITLE}" '
            f'buttons {{"OK"}} default button "OK"',
        ],
        capture_output=True,
    )
    if wait_user and result.returncode != 0:
        raise RuntimeError("User cancelled.")


def _launch_chrome(url: str) -> subprocess.Popen:
    """Launch Chrome with CDP enabled and a dedicated user profile."""
    CHROME_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen([
        CHROME_BIN,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={CHROME_PROFILE_DIR}",
        "--start-maximized",
        url,
    ])


def _extract_session_via_cdp() -> tuple[list[dict], TokenData | None]:
    """Connect to running Chrome via CDP and extract cookies + Auth0 token."""
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        context = browser.contexts[0]
        pages = context.pages

        dashboard_page = next(
            (pg for pg in pages if DASHBOARD_URL in pg.url),
            pages[0] if pages else None,
        )

        if not dashboard_page:
            return [], None

        raw_token = dashboard_page.evaluate("""
            () => {
                const auth0Key = Object.keys(localStorage)
                    .find(k => k.startsWith('@@auth0spajs@@'));
                return {
                    auth0: auth0Key ? JSON.parse(localStorage[auth0Key]) : null,
                    localStorage: Object.fromEntries(
                        Object.keys(localStorage).map(k => [k, localStorage[k]])
                    ),
                };
            }
        """)

        cookies = context.cookies(ESENCIAL_COOKIE_DOMAINS)
        browser.close()

    return cookies, _format_token(raw_token) if raw_token else None


def _format_token(raw: dict) -> TokenData:
    """Normalize the Auth0 token data extracted from localStorage."""
    auth0 = raw.get("auth0") or {}
    body = auth0.get("body") or {}
    ls = raw.get("localStorage") or {}

    fallback_token = None
    raw_app_token = ls.get("AuthAccessToken")
    if raw_app_token:
        try:
            fallback_token = json.loads(raw_app_token).get("access_token")
        except (ValueError, TypeError):
            pass

    return {
        "access_token": body.get("access_token") or fallback_token,
        "expires_at": auth0.get("expiresAt"),
        "datadome_client_id": ls.get("ddSession"),
        "local_storage": ls,
    }
