import json
import os
import pytest
from unittest.mock import MagicMock, patch, Mock
from io import BytesIO
from agent import handle_tool_call, run_agent


def test_get_weather():
    result = json.loads(handle_tool_call("get_weather", {"city": "Tokyo"}))
    assert result["city"] == "Tokyo"
    assert "temp_c" in result
    assert "condition" in result


def test_calculate():
    result = json.loads(handle_tool_call("calculate", {"expression": "2 + 3 * 4"}))
    assert result["result"] == 14


def test_calculate_bad_expression():
    result = json.loads(handle_tool_call("calculate", {"expression": "import os"}))
    assert "error" in result


def test_unknown_tool():
    result = json.loads(handle_tool_call("nonexistent", {}))
    assert "error" in result


def test_read_file_success(tmp_path):
    test_file = tmp_path / "hello.txt"
    test_file.write_text("hello world", encoding="utf-8")
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        result = json.loads(handle_tool_call("read_file", {"file_path": "hello.txt"}))
        assert result["content"] == "hello world"
    finally:
        os.chdir(original_dir)


def test_read_file_not_found():
    result = json.loads(handle_tool_call("read_file", {"file_path": "nonexistent.txt"}))
    assert "error" in result
    assert "not found" in result["error"]


def test_read_file_path_traversal():
    result = json.loads(handle_tool_call("read_file", {"file_path": "../secret.txt"}))
    assert result["error"] == "Path not allowed"


def test_read_file_absolute_path():
    result = json.loads(handle_tool_call("read_file", {"file_path": "/etc/passwd"}))
    assert result["error"] == "Path not allowed"


def test_run_agent_end_turn():
    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [MagicMock(text="Hello!", spec=["text"])]

    with patch("agent.client.messages.create", return_value=mock_response):
        result = run_agent("Say hello")
    assert result == "Hello!"


def test_web_fetch_blocks_non_https():  # AC3 KAN-6
    result = json.loads(handle_tool_call("web_fetch", {"url": "file:///etc/passwd"}))
    assert "error" in result
    assert "Only http and https" in result["error"]


def test_web_fetch_blocks_ftp():  # AC3 KAN-6
    result = json.loads(handle_tool_call("web_fetch", {"url": "ftp://example.com/file"}))
    assert "error" in result


def test_web_fetch_returns_structured_json():  # AC2 KAN-6
    mock_resp = Mock()
    mock_resp.status = 200
    mock_resp.read.return_value = b"<html>hello</html>"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = Mock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = json.loads(handle_tool_call("web_fetch", {"url": "https://example.com"}))

    assert result["url"] == "https://example.com"
    assert result["status_code"] == 200
    assert "content" in result


def test_web_fetch_truncates_to_4000_chars():  # AC4 KAN-6
    long_content = b"x" * 10000
    mock_resp = Mock()
    mock_resp.status = 200
    mock_resp.read.return_value = long_content
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = Mock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = json.loads(handle_tool_call("web_fetch", {"url": "https://example.com"}))

    assert len(result["content"]) <= 4000


if __name__ == "__main__":
    test_get_weather()
    test_calculate()
    test_calculate_bad_expression()
    test_unknown_tool()
    test_run_agent_end_turn()
    print("All tests passed (run via pytest for full coverage).")
