import anthropic
import datetime
import json
import os


client = anthropic.Anthropic()

TOOLS = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"],
        },
    },
    {
        "name": "calculate",
        "description": "Perform a basic math calculation",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression e.g. '2 + 3 * 4'"}
            },
            "required": ["expression"],
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file by path (relative to the working directory)",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Relative path to the file"}
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "get_current_date",
        "description": "Get the current date and time in ISO 8601 format",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Optional timezone name (e.g. 'UTC', 'US/Eastern'). Defaults to UTC.",
                }
            },
            "required": [],
        },
    },
]


def handle_tool_call(name: str, inputs: dict) -> str:
    if name == "get_weather":
        city = inputs["city"]
        # Stub response
        return json.dumps({"city": city, "temp_c": 22, "condition": "Sunny"})
    elif name == "calculate":
        try:
            result = eval(inputs["expression"], {"__builtins__": {}})
            return json.dumps({"result": result})
        except Exception as e:
            return json.dumps({"error": str(e)})
    elif name == "read_file":
        file_path = inputs["file_path"]
        if ".." in file_path or os.path.isabs(file_path) or file_path.startswith("/"):
            return json.dumps({"error": "Path not allowed"})
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.dumps({"content": f.read()})
        except FileNotFoundError:
            return json.dumps({"error": f"File not found: {file_path}"})
        except PermissionError:
            return json.dumps({"error": f"Permission denied: {file_path}"})
    elif name == "get_current_date":
        tz_name = inputs.get("timezone", "UTC")
        try:
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            return json.dumps({"datetime_utc": now, "timezone_requested": tz_name})
        except Exception as e:
            return json.dumps({"error": str(e)})
    return json.dumps({"error": "Unknown tool"})


def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = handle_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "Agent stopped unexpectedly."


if __name__ == "__main__":
    prompts = [
        "What's the weather like in Tokyo?",
        "What is 15 * 8 + 42?",
        "What's the weather in Paris and what is 100 / 4?",
    ]
    for prompt in prompts:
        print(f"\nUser: {prompt}")
        print(f"Agent: {run_agent(prompt)}")
