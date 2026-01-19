---
name: agents-sdk-multiagent-builder
description: Build production-grade multi-agent workflows using the OpenAI Agents SDK (Python). Use when asked to design and generate an agentic system (plan + runnable scaffold) with handoffs, sessions/memory, function tools, context management, input/output guardrails, structured outputs, dynamic instructions, streaming, agents-as-tool composition, custom model configuration, MCP integrations, tracing/observability, and robust error handling.
---

# Agents SDK Multi-Agent Builder

## Workflow (do this whenever the skill triggers)

### 0) Confirm success criteria (one sentence)
- Restate the user’s goal as: **"Produce a production-grade multi-agent plan + implement a runnable scaffold using OpenAI Agents SDK (Python), customized to requirements."**

### 1) Gather requirements (ask only what you need)
Ask 3–6 targeted questions (use AskUserQuestion if available):
- Primary product surface (CLI / API service / background worker / notebook).
- External integrations (APIs, DB, files), auth needs, and data sensitivity.
- Needed specialist agents (roles) and routing policy.
- Output format needs (free-text vs structured output models).
- Guardrails policy (allowed/blocked content, PII rules, refusal policy).
- Observability needs (tracing destination, logging).

If the user already provided a spec, do not re-ask; proceed.

### 2) Verify SDK APIs (do not rely on memory)
Before writing code, fetch up-to-date names/examples:
- Prefer Context7: resolve `/openai/openai-agents-python` (or the website mirror) and query docs.
- Or use the canonical docs URLs listed in `references/api_reference.md`.

### 3) Produce a “production-grade plan” artifact (keep it crisp)
Output a plan with this structure:
1. **Scope** (in/out) + assumptions
2. **Agent inventory** (name → responsibilities → inputs/outputs)
3. **Routing & handoffs** (triage policy, escalation rules)
4. **Tools** (each tool: purpose, schema, side effects, error modes)
5. **Context strategy** (what persists, session keys, what’s excluded)
6. **Guardrails** (input + output; tripwire policy; remediation)
7. **Structured outputs** (Pydantic models + validation points)
8. **MCP integration** (servers, tool caching, trust boundaries)
9. **Observability** (tracing, logs, metrics, correlation IDs)
10. **Failure handling** (SDK exceptions, retries, max turns, fallbacks)
11. **Test plan** (unit tests for tools, guardrails, routing; smoke run)

### 4) Generate the runnable scaffold from the plan
Create a minimal multi-file Python project that matches the plan.

**Default scaffold (recommended):**
```
<project-root>/
  pyproject.toml
  src/<app_name>/
    __init__.py
    config.py
    models.py
    tools.py
    guardrails.py
    mcp_servers.py
    agents.py
    runner.py
  tests/
    test_tools.py
    test_guardrails.py
```

Notes:
- Keep the diff small and focused: only add files required by the plan.
- Prefer `src/` layout.

### 5) Implementation rules (quality bar)
- Prefer typed structured outputs with Pydantic `BaseModel` via `output_type=...` when outputs need reliability.
- Put all external I/O behind tools (DB/network/files). Keep agents “pure” where possible.
- Treat MCP as untrusted boundary; use guardrails/validation on tool outputs.
- Centralize configuration (API keys, model names) in `config.py` (never hardcode secrets).

### 6) Acceptance checks (must include)
Include a checklist the user can run:
- [ ] `pip install openai-agents` (or `uv add openai-agents`)
- [ ] `OPENAI_API_KEY` is set
- [ ] `python -m <app_name>.runner` runs a smoke prompt
- [ ] Guardrail tripwire test cases pass
- [ ] Tool unit tests pass

## Canonical implementation patterns (copy/paste, then adapt)

### Agent + Runner
```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="...",
)

result = await Runner.run(agent, "Hello")
print(result.final_output)
```

### Sessions (SQLiteSession)
```python
from agents import Agent, Runner, SQLiteSession

session = SQLiteSession("conversation_123")
result = await Runner.run(agent, "Hello", session=session)
```

### Function tools
```python
from agents import function_tool

@function_tool
async def my_tool(arg: dict) -> str:
    return "ok"
```

### Handoffs
```python
from agents import Agent, handoff

specialist = Agent(name="Specialist", instructions="...")
triage = Agent(name="Triage", instructions="...", handoffs=[handoff(specialist)])
```

### Structured outputs
```python
from pydantic import BaseModel
from agents import Agent

class Output(BaseModel):
    answer: str

agent = Agent(name="...", instructions="...", output_type=Output)
```

### Input guardrails (tripwire)
Use an `InputGuardrail(...)` that returns `GuardrailFunctionOutput(tripwire_triggered=...)`.
See `references/api_reference.md` for a verified example and exception types.

### Output guardrails (tripwire)
Use `@output_guardrail` (or `OutputGuardrail(...)`) and handle `OutputGuardrailTripwireTriggered`.

### Streaming
```python
from agents import Runner

result = Runner.run_streamed(agent, input="Hello")
async for event in result.stream_events():
    ...
```

### Agents-as-tools composition
```python
orchestrator = Agent(
    name="Orchestrator",
    tools=[some_agent.as_tool(tool_name="delegate", tool_description="...")],
)
```

### MCP integration
```python
from agents.mcp import MCPServerStreamableHttp

async with MCPServerStreamableHttp(
    name="My HTTP Server",
    params={"url": "http://localhost:8000/mcp"},
    cache_tools_list=True,
) as server:
    agent = Agent(name="Assistant", mcp_servers=[server])
```

### Tracing
Use `set_tracing_export_api_key(...)` to export traces. See `references/api_reference.md` for exact snippet.

## What to do when the user says “include any feature”
Treat “feature” as an extension point in the plan:
- Add/modify agents (new responsibilities)
- Add tools (new side effects)
- Add/modify structured outputs (new schemas)
- Add guardrails (new safety/business rules)
- Add MCP servers (new capabilities)
- Expand tests (new acceptance checks)

## Resources
- Read `references/api_reference.md` to verify exact imports, exception names, and canonical links.
