"""Interactive login flow using real Chrome + CDP for session extraction.

Launches Chrome with remote debugging enabled. After the user completes
authentication (RUT, password, captcha, 2FA), connects via CDP to extract
cookies and the Auth0 access token from localStorage.
"""

from concurrent.futures import ThreadPoolExecutor

from playwright.sync_api import sync_playwright

from esencial.auth.messages import (
    DIALOG_TITLE,
    ERR_EXTRACT_SESSION,
    ERR_NO_CREDENTIALS,
    LOGIN_PROMPT,
    SESSION_SAVED,
)
from esencial.auth.models import SessionData
from esencial.auth.session import save_session
from esencial.auth.system import launch_chrome, show_dialog
from esencial.config import CDP_PORT, DASHBOARD_URL, LOGIN_URL

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
        True on success, False if credential extraction failed.
    """
    proc = launch_chrome(LOGIN_URL)
    try:
        show_dialog(LOGIN_PROMPT, DIALOG_TITLE)
        with ThreadPoolExecutor(max_workers=1) as ex:
            session_data = ex.submit(_extract_session_via_cdp).result()

        if not session_data or not session_data.cookies or not session_data.token.access_token:
            show_dialog(ERR_NO_CREDENTIALS, DIALOG_TITLE)
            return False

        save_session(session_data)
        show_dialog(SESSION_SAVED, DIALOG_TITLE)
        return True

    except Exception as e:
        show_dialog(ERR_EXTRACT_SESSION.format(error=e), DIALOG_TITLE)
        return False
    finally:
        proc.terminate()


def _extract_session_via_cdp() -> SessionData | None:
    """Connect to running Chrome via CDP and extract a SessionData."""
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        context = browser.contexts[0]
        pages = context.pages

        dashboard_page = next(
            (pg for pg in pages if DASHBOARD_URL in pg.url),
            pages[0] if pages else None,
        )

        if not dashboard_page:
            return None

        raw = dashboard_page.evaluate("""
            () => {
                const auth0Key = Object.keys(localStorage)
                    .find(k => k.startsWith('@@auth0spajs@@'));
                return {
                    auth0: auth0Key ? JSON.parse(localStorage[auth0Key]) : {},
                    localStorage: Object.fromEntries(
                        Object.keys(localStorage).map(k => [k, localStorage[k]])
                    ),
                };
            }
        """)

        cookies = context.cookies(ESENCIAL_COOKIE_DOMAINS)
        browser.close()

    return SessionData.from_browser_data(cookies, raw)
