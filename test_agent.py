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


def test_get_current_date():
    result = json.loads(handle_tool_call("get_current_date", {}))
    assert "datetime_utc" in result
    assert "T" in result["datetime_utc"]


def test_get_current_date_with_timezone():
    result = json.loads(handle_tool_call("get_current_date", {"timezone": "US/Eastern"}))
    assert "datetime_utc" in result
    assert result["timezone_requested"] == "US/Eastern"


def test_read_file_permission_error(tmp_path):
    test_file = tmp_path / "locked.txt"
    test_file.write_text("secret", encoding="utf-8")
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        with patch("builtins.open", side_effect=PermissionError("denied")):
            result = json.loads(handle_tool_call("read_file", {"file_path": "locked.txt"}))
        assert "error" in result
        assert "Permission denied" in result["error"]
    finally:
        os.chdir(original_dir)


def test_run_agent_end_turn():
    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [MagicMock(text="Hello!", spec=["text"])]

    with patch("agent.client.messages.create", return_value=mock_response):
        result = run_agent("Say hello")
    assert result == "Hello!"


def test_run_agent_tool_use_then_end_turn():
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "get_current_date"
    tool_block.input = {}
    tool_block.id = "tool_123"

    tool_response = MagicMock()
    tool_response.stop_reason = "tool_use"
    tool_response.content = [tool_block]

    end_block = MagicMock(spec=["text"])
    end_block.text = "The current date is 2026-06-26."
    end_response = MagicMock()
    end_response.stop_reason = "end_turn"
    end_response.content = [end_block]

    with patch("agent.client.messages.create", side_effect=[tool_response, end_response]):
        result = run_agent("What is today's date?")
    assert "2026" in result or result == "The current date is 2026-06-26."


def test_run_agent_unexpected_stop():
    mock_response = MagicMock()
    mock_response.stop_reason = "max_tokens"
    mock_response.content = []

    with patch("agent.client.messages.create", return_value=mock_response):
        result = run_agent("Say something")
    assert result == "Agent stopped unexpectedly."


if __name__ == "__main__":
    test_get_weather()
    test_calculate()
    test_calculate_bad_expression()
    test_unknown_tool()
    test_run_agent_end_turn()
    print("All tests passed (run via pytest for full coverage).")
