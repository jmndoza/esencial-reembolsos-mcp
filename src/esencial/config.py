"""Shared configuration constants."""

from pathlib import Path

# Esencial URLs
LOGIN_URL = "https://auth.somosesencial.cl/login"
DASHBOARD_URL = "https://sucursalvirtual.somosesencial.cl"
API_BASE_URL = "https://api-sucursalvirtual.somosesencial.cl"

# Chrome
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROME_PROFILE_DIR = Path.home() / ".esencial" / "chrome-profile"
CDP_PORT = 9222
