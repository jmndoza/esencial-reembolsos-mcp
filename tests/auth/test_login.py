from unittest.mock import MagicMock, patch

from esencial.auth.login import login
from esencial.auth.models import Cookie, LocalStorage, SessionData, TokenInfo


def _valid_session() -> SessionData:
    return SessionData(
        cookies=[Cookie(name="c", value="v")],
        token=TokenInfo(access_token="abc", expires_at=1),
        local_storage=LocalStorage(),
    )


def _empty_session() -> SessionData:
    return SessionData(
        cookies=[],
        token=TokenInfo(access_token=None, expires_at=None),
        local_storage=LocalStorage(),
    )


def test_login_saves_session_and_returns_true_on_success():
    with patch("esencial.auth.login.launch_chrome", return_value=MagicMock()), \
         patch("esencial.auth.login.show_dialog"), \
         patch(
             "esencial.auth.login._extract_session_via_cdp",
             return_value=_valid_session(),
         ), \
         patch("esencial.auth.login.save_session") as mock_save:
        result = login()

    assert result is True
    mock_save.assert_called_once()


def test_login_returns_false_and_skips_save_when_credentials_missing():
    with patch("esencial.auth.login.launch_chrome", return_value=MagicMock()), \
         patch("esencial.auth.login.show_dialog"), \
         patch(
             "esencial.auth.login._extract_session_via_cdp",
             return_value=_empty_session(),
         ), \
         patch("esencial.auth.login.save_session") as mock_save:
        result = login()

    assert result is False
    mock_save.assert_not_called()


def test_login_terminates_chrome_process_even_on_failure():
    proc = MagicMock()
    with patch("esencial.auth.login.launch_chrome", return_value=proc), \
         patch("esencial.auth.login.show_dialog"), \
         patch(
             "esencial.auth.login._extract_session_via_cdp",
             return_value=_empty_session(),
         ), \
         patch("esencial.auth.login.save_session"):
        login()

    proc.terminate.assert_called_once()
