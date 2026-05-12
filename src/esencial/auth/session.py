"""Session persistence using macOS Keychain."""

import keyring
from keyring.errors import PasswordDeleteError
from pydantic import ValidationError

from esencial.auth.models import SessionData

KEYRING_SERVICE = "esencial-reembolsos"
KEYRING_USERNAME = "session"


def save_session(session_data: SessionData) -> None:
    """Save session data to the macOS Keychain."""
    keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, session_data.model_dump_json())


def load_session() -> SessionData | None:
    """Load saved session data, or None if no session exists or it's malformed."""
    raw = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    if not raw:
        return None
    try:
        return SessionData.model_validate_json(raw)
    except ValidationError:
        return None


def clear_session() -> None:
    """Remove the saved session from the Keychain.

    Silently succeeds if there is no session to delete.
    """
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except PasswordDeleteError:
        pass
