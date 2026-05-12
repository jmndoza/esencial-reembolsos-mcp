"""HTTP client for the Esencial API.

Uses curl-cffi to impersonate Chrome's TLS fingerprint and bypass DataDome blocks.
"""

from esencial.auth.login import login
from esencial.auth.models import SessionData
from esencial.auth.session import load_session
from esencial.client import endpoints
from esencial.client.base import HttpClient
from esencial.config import API_BASE_URL, DASHBOARD_URL

DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-CL,es;q=0.9",
    "Origin": DASHBOARD_URL,
    "Referer": f"{DASHBOARD_URL}/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}


def _build_auth_headers(session: SessionData) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {session.token.access_token or ''}",
        "X-Datadome-Clientid": session.local_storage.dd_session or "",
    }


class EsencialClient(HttpClient):
    """Esencial HTTP client with auth headers and Chrome TLS impersonation."""

    def __init__(self):
        super().__init__(base_url=API_BASE_URL, impersonate="chrome120")
        self._load_auth()

    def _load_auth(self) -> bool:
        """Read the saved session and apply cookies + auth headers.

        Returns True on success. Raises RuntimeError if no session exists.
        """
        session = load_session()
        if not session:
            raise RuntimeError("No saved session. Run auth first.")
        self.headers.update({**DEFAULT_HEADERS, **_build_auth_headers(session)})
        self.cookies.update(session.cookies_as_dict)
        return True

    def _handle_client_error(self, response) -> bool:
        if response.status_code not in (401, 403):
            return False
        return login() and self._load_auth()

    def download_file(self, document_id: str) -> bytes:
        """Download a file by its document ID."""
        r = self.get(
            endpoints.AFFILIATE_FILE.format(document_id=document_id),
            headers={"Accept": "application/pdf"},
        )
        return r.content

    @classmethod
    def ensure_session(cls) -> "EsencialClient":
        """Construct a client, triggering login if no session is saved."""
        if not load_session():
            login()
        return cls()
