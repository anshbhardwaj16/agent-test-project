import anthropic
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone


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
        "name": "web_fetch",
        "description": "Fetch the content of a public URL and return its text content",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The http or https URL to fetch"}
            },
            "required": ["url"],
        },
    },
    {
        "name": "get_current_time",
        "description": "Get the current live time with high precision",
        "input_schema": {
            "type": "object",
            "properties": {},
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
    elif name == "web_fetch":
        url = inputs["url"]
        if not url.startswith("http://") and not url.startswith("https://"):
            return json.dumps({"error": "Only http and https URLs are allowed"})
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8", errors="replace")
            return json.dumps({
                "url": url,
                "status_code": resp.status,
                "content": content[:4000],
            })
        except urllib.error.HTTPError as e:
            return json.dumps({"error": f"HTTP {e.code}: {e.reason}", "url": url})
        except Exception as e:
            return json.dumps({"error": str(e), "url": url})
    elif name == "get_current_time":
        now = datetime.now(timezone.utc)
        return json.dumps({
            "utc_time": now.isoformat().replace("+00:00", "Z"),
            "unix_timestamp": now.timestamp(),
            "readable": now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC",
        })
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
