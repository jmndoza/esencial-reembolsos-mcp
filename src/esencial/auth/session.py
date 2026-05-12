"""Session persistence using macOS Keychain."""

import json

import keyring
from keyring.errors import PasswordDeleteError

from esencial.auth.models import SessionData, TokenData

KEYRING_SERVICE = "esencial-reembolsos"
KEYRING_USERNAME = "session"


def save_session(cookies: list[dict], token_data: TokenData) -> None:
    """Save cookies and Auth0 token data to the macOS Keychain."""
    data: SessionData = {"cookies": cookies, "token_data": token_data}
    keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, json.dumps(data))


def load_session() -> SessionData | None:
    """Load saved session data, or None if no session exists."""
    raw = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    return json.loads(raw) if raw else None


def clear_session() -> None:
    """Remove the saved session from the Keychain.

    Silently succeeds if there is no session to delete.
    """
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except PasswordDeleteError:
        pass
