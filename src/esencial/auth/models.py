"""Data models for the auth domain."""

import json
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator


class OmnitokAffiliate(BaseModel):
    """Subset of the `omnitok-affiliate` JSON stored in localStorage."""

    rut: str | None = None


class SelectedAffiliate(BaseModel):
    """Subset of the `SELECTED_AFFILIATE` JSON stored in localStorage."""

    rutPar: str | None = None


class AuthAccessToken(BaseModel):
    """Subset of the `AuthAccessToken` JSON stored in localStorage."""

    access_token: str | None = None


def _parse_json(value):
    """BeforeValidator: parse a JSON-encoded string; return None on failure."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return None
    return value


JsonObject = BeforeValidator(_parse_json)


class Cookie(BaseModel):
    """A cookie name/value pair."""

    model_config = ConfigDict(extra="ignore")

    name: str
    value: str


class LocalStorage(BaseModel):
    """Modeled subset of the browser's localStorage (other keys ignored)."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    dd_session: str | None = Field(None, alias="ddSession")
    omnitok_affiliate: Annotated[OmnitokAffiliate | None, JsonObject] = Field(
        None, alias="omnitok-affiliate"
    )
    selected_affiliate: Annotated[SelectedAffiliate | None, JsonObject] = Field(
        None, alias="SELECTED_AFFILIATE"
    )
    auth_access_token: Annotated[AuthAccessToken | None, JsonObject] = Field(
        None, alias="AuthAccessToken"
    )

    @property
    def affiliate_rut(self) -> str | None:
        """The affiliate's RUT, taken from whichever localStorage source has it."""
        return (
            getattr(self.omnitok_affiliate, "rut", None)
            or getattr(self.selected_affiliate, "rutPar", None)
        )


class TokenInfo(BaseModel):
    """Auth0 access token data."""

    access_token: str | None
    expires_at: int | None


class SessionData(BaseModel):
    """Full session payload persisted in the Keychain."""

    cookies: list[Cookie]
    token: TokenInfo
    local_storage: LocalStorage

    @property
    def cookies_as_dict(self) -> dict[str, str]:
        """Cookies as a {name: value} dict, suitable for HTTP session use."""
        return {cookie.name: cookie.value for cookie in self.cookies}

    @field_validator("cookies", mode="before")
    @classmethod
    def _normalize_cookies(cls, value):
        """Accept a dict[name, value] for backward compat; convert to list of Cookie."""
        if isinstance(value, dict):
            return [{"name": k, "value": v} for k, v in value.items()]
        return value

    @classmethod
    def from_browser_data(cls, cookies, raw: dict) -> "SessionData":
        """Build a SessionData from raw browser data.

        Args:
            cookies: Playwright cookie list (or already-normalized list of Cookie dicts).
            raw: JS evaluation result with shape {auth0, localStorage}.
        """
        auth0 = raw["auth0"]
        body = auth0.get("body", {})
        local_storage = LocalStorage.model_validate(raw["localStorage"])
        token = TokenInfo(
            access_token=body.get("access_token")
            or getattr(local_storage.auth_access_token, "access_token", None),
            expires_at=auth0.get("expiresAt"),
        )
        return cls(cookies=cookies, token=token, local_storage=local_storage)
