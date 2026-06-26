---
omnispark:
  schema: readme/v1
  repo_key: agent-test-project
  type: unknown
  primary_languages: [python]
  cloud: unknown
  migration_role: n/a
  owns:
    entity_types: []
    source_systems: []
    artifacts:
      - src/agent_test_project
    containers: []
    pyfunctions: []
    endpoints: []
    schemas: []
  depends_on: []
  provides_to: []
  routing_keywords:
    - test
    - agent
    - project
    - omnispark
    - agent test project
    - agent-test-project
  out_of_scope: []
---
# agent-test-project

> Minimal Claude tool-use agent demonstrating the agentic loop pattern with the Anthropic Python SDK.

## What this is

A self-contained Python script (`agent.py`) that wires stub tools — `get_weather`, `calculate`, `read_file`, and `get_current_date` — into a Claude `tool_use` agentic loop. The loop runs until `stop_reason == "end_turn"`, dispatching tool calls via `handle_tool_call()` and feeding results back as `tool_result` messages. The project exists as a reference implementation and test bed for the tool-use pattern using `claude-sonnet-4-6`.

There are no services, no containers, and no external dependencies beyond the Anthropic SDK. All tool responses are stubs (hardcoded weather data, `eval`-based math with a safe builtins context).

## What it owns

- **Entry point**: `agent.py` — agent loop + tool definitions + stub handlers (`get_weather`, `calculate`, `read_file`, `get_current_date`)
- **Tests**: `test_agent.py` — pytest suite covering tool handlers and the mocked agent loop
- **Runtime credential**: `ANTHROPIC_API_KEY` (read by `anthropic.Anthropic()` at line 5)

## How it relates to other repos in the workspace

Standalone — no in-workspace dependencies declared yet.

## Quickstart

```bash
git clone <repo-url> agent-test-project
cd agent-test-project
pip install -r requirements.txt
export ANTHROPIC_API_KEY=<your-key>
python agent.py          # runs three sample prompts
pytest test_agent.py     # runs unit tests (no API key needed — mocked)
```

## Validate this repo

```bash
python ../omnispark/scripts/validate_repo_docs.py --repo agent-test-project
```

The pre-commit hook runs this automatically when README or
CONTRIBUTING is in the commit (see [CONTRIBUTING.md](CONTRIBUTING.md#pre-commit-gate)).

## See also

- [CONTRIBUTING.md](CONTRIBUTING.md) — branch / PR / convention rules
- [.omnispark/memory.md](.omnispark/memory.md) — repo-specific notes
- [Workspace manifest](../.workspace/workspace.json) — sibling repos
- [Workspace architecture](../.workspace/architecture.md) — AWS→GCP migration
- [Framework docs](../omnispark/docs/) — slash command reference
