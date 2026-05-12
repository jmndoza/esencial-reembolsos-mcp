"""Native OS integrations for the auth flow."""

import subprocess

from esencial.config import CDP_PORT, CHROME_BIN, CHROME_PROFILE_DIR


def show_dialog(message: str, title: str) -> None:
    """Show a native macOS dialog with an OK button. Blocks until clicked."""
    safe = message.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(
        [
            "osascript", "-e",
            f'display dialog "{safe}" with title "{title}" '
            f'buttons {{"OK"}} default button "OK"',
        ],
        capture_output=True,
    )


def launch_chrome(url: str) -> subprocess.Popen:
    """Launch Chrome with CDP enabled and a dedicated user profile."""
    CHROME_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen([
        CHROME_BIN,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={CHROME_PROFILE_DIR}",
        "--start-maximized",
        url,
    ])
