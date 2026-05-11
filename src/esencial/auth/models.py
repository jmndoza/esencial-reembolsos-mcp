"""Data models for the auth domain."""

from typing import TypedDict


class TokenData(TypedDict):
    """Normalized Auth0 token data extracted from the browser."""
    access_token: str | None
    expires_at: int | None
    datadome_client_id: str | None
    local_storage: dict[str, str]


class SessionData(TypedDict):
    """Full session payload persisted in the Keychain."""
    cookies: list[dict]
    token_data: TokenData
