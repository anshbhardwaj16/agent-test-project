import json
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
    print("All tests passed.")
