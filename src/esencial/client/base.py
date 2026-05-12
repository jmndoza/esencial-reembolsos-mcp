"""Generic HTTP client base."""

from urllib.parse import urljoin

from curl_cffi.requests import Session
from curl_cffi.requests.exceptions import HTTPError


class HttpClient(Session):
    """curl_cffi Session with base_url support and a retry-on-error hook.

    Subclasses override `_handle_client_error` to react to 4XX/5XX responses
    (e.g., refresh credentials, back off). When the hook returns True, the
    request is retried once.
    """

    def __init__(self, base_url: str, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url

    def request(self, method, url, **kwargs):
        url = urljoin(self.base_url, url)
        return self._send_with_retry(method, url, **kwargs)

    def _send_with_retry(self, method, url, **kwargs):
        """Send a request, retry once if `_handle_client_error` allows it."""
        try:
            r = super().request(method, url, **kwargs)
            r.raise_for_status()
        except HTTPError as e:
            if not self._handle_client_error(e.response):
                raise
            r = super().request(method, url, **kwargs)
            r.raise_for_status()
        return r

    def _handle_client_error(self, response) -> bool:
        """Override to react to HTTP errors. Return True to retry the request."""
        return False
