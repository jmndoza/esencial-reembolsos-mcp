from unittest.mock import patch

from esencial.auth.system import launch_chrome, show_dialog


def test_show_dialog_calls_osascript_with_message_and_title():
    with patch("esencial.auth.system.subprocess.run") as mock_run:
        show_dialog("Hello", "MyApp")
        argv = mock_run.call_args[0][0]
        cmd = argv[2]
        assert argv[0] == "osascript"
        assert "Hello" in cmd
        assert "MyApp" in cmd


def test_show_dialog_escapes_double_quotes():
    with patch("esencial.auth.system.subprocess.run") as mock_run:
        show_dialog('he said "hi"', "X")
        cmd = mock_run.call_args[0][0][2]
        assert '\\"hi\\"' in cmd


def test_launch_chrome_includes_cdp_port_and_url(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "esencial.auth.system.CHROME_PROFILE_DIR", tmp_path / "chrome-profile"
    )
    with patch("esencial.auth.system.subprocess.Popen") as mock_popen:
        launch_chrome("https://example.com")
        argv = mock_popen.call_args[0][0]
        assert any("--remote-debugging-port" in arg for arg in argv)
        assert "https://example.com" in argv
