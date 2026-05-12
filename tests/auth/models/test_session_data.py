import json

from esencial.auth.models import LocalStorage, SessionData, TokenInfo


def _token() -> TokenInfo:
    return TokenInfo(access_token="tk", expires_at=1)


def _local_storage() -> LocalStorage:
    return LocalStorage()


def test_cookies_validator_accepts_playwright_list():
    raw_cookies = [
        {"name": "session_id", "value": "abc", "domain": ".somosesencial.cl"},
        {"name": "datadome", "value": "xyz"},
    ]
    session = SessionData(cookies=raw_cookies, token=_token(), local_storage=_local_storage())
    assert len(session.cookies) == 2
    assert session.cookies[0].name == "session_id"
    assert session.cookies[0].value == "abc"


def test_cookies_validator_accepts_dict_format():
    session = SessionData(
        cookies={"foo": "bar"},
        token=_token(),
        local_storage=_local_storage(),
    )
    assert len(session.cookies) == 1
    assert session.cookies[0].name == "foo"
    assert session.cookies[0].value == "bar"


def test_from_browser_data_builds_full_session():
    raw = {
        "auth0": {
            "body": {"access_token": "auth0-token"},
            "expiresAt": 1234567890,
        },
        "localStorage": {
            "ddSession": "dd-id",
            "omnitok-affiliate": json.dumps({"rut": "11111111-1"}),
        },
    }
    cookies = [{"name": "c", "value": "v"}]
    session = SessionData.from_browser_data(cookies, raw)

    assert len(session.cookies) == 1
    assert session.cookies[0].name == "c"
    assert session.token.access_token == "auth0-token"
    assert session.token.expires_at == 1234567890
    assert session.local_storage.dd_session == "dd-id"
    assert session.local_storage.affiliate_rut == "11111111-1"


def test_from_browser_data_falls_back_to_auth_access_token():
    raw = {
        "auth0": {"body": {}, "expiresAt": 999},
        "localStorage": {
            "AuthAccessToken": json.dumps({"access_token": "fallback-token"}),
        },
    }
    session = SessionData.from_browser_data([], raw)
    assert session.token.access_token == "fallback-token"


def test_from_browser_data_handles_empty_browser_state():
    raw = {"auth0": {}, "localStorage": {}}
    session = SessionData.from_browser_data([], raw)

    assert session.cookies == []
    assert session.token.access_token is None
    assert session.token.expires_at is None
    assert session.local_storage.dd_session is None
    assert session.local_storage.affiliate_rut is None
