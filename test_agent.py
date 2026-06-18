import json
import os
import pytest
from unittest.mock import MagicMock, patch
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


if __name__ == "__main__":
    test_get_weather()
    test_calculate()
    test_calculate_bad_expression()
    test_unknown_tool()
    test_run_agent_end_turn()
    print("All tests passed (run via pytest for full coverage).")
