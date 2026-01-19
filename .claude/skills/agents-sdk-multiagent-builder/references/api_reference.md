# OpenAI Agents SDK (Python) – Verified Quick Reference

Keep this file short and use it to **verify exact names** before writing scaffold code.

## Canonical docs
- Sessions: https://openai.github.io/openai-agents-python/sessions/
- Handoffs: https://openai.github.io/openai-agents-python/handoffs/
- Tools: https://openai.github.io/openai-agents-python/tools/
- Context strategies: https://openai.github.io/openai-agents-python/context/
- Guardrails: https://openai.github.io/openai-agents-python/guardrails/
- Streaming: https://openai.github.io/openai-agents-python/streaming/
- MCP: https://openai.github.io/openai-agents-python/mcp/
- Tracing: https://openai.github.io/openai-agents-python/tracing/
- Running agents: https://openai.github.io/openai-agents-python/running_agents/

## Install
- Package name: `openai-agents`

## Core imports (common)
```python
from agents import Agent, Runner
from agents import function_tool
from agents import handoff
from agents import SQLiteSession
```

## Run an agent
```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="...")
result = await Runner.run(agent, "Hello")
print(result.final_output)
```

## Run with a session
```python
from agents import SQLiteSession, Runner

session = SQLiteSession("conversation_123")
result = await Runner.run(agent, "Hello", session=session)
```

## Streaming
```python
from agents import Runner

result = Runner.run_streamed(agent, input="Hello")
async for event in result.stream_events():
    # event.type may include: raw_response_event, agent_updated_stream_event, run_item_stream_event
    ...
```

## Function tool
```python
from agents import function_tool

@function_tool
async def fetch_weather(location: dict) -> str:
    return "sunny"
```

## Handoff
```python
from agents import Agent, handoff

agent_a = Agent(name="Billing agent")
agent_b = Agent(name="Refund agent")
triage = Agent(name="Triage agent", handoffs=[agent_a, handoff(agent_b)])
```

## Guardrails (exception names)
From docs, the runner can raise exceptions inheriting from `AgentsException`, including:
- `MaxTurnsExceeded`
- `ModelBehaviorError`
- `UserError`
- `InputGuardrailTripwireTriggered`
- `OutputGuardrailTripwireTriggered`

### Input guardrail pattern (verified example)
```python
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from agents.exceptions import InputGuardrailTripwireTriggered

async def my_input_guardrail(ctx, agent, input_data):
    # return GuardrailFunctionOutput(...)
    return GuardrailFunctionOutput(output_info=None, tripwire_triggered=False)

agent = Agent(
    name="Triage",
    instructions="...",
    input_guardrails=[InputGuardrail(guardrail_function=my_input_guardrail)],
)

try:
    await Runner.run(agent, "Hello")
except InputGuardrailTripwireTriggered:
    ...
```

### Output guardrail pattern (verified example)
```python
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)

@output_guardrail
async def my_output_guardrail(ctx: RunContextWrapper, agent: Agent, output):
    return GuardrailFunctionOutput(output_info=None, tripwire_triggered=False)

agent = Agent(
    name="Assistant",
    instructions="...",
    output_guardrails=[my_output_guardrail],
)

try:
    await Runner.run(agent, "Hello")
except OutputGuardrailTripwireTriggered:
    ...
```

## Structured outputs
```python
from pydantic import BaseModel
from agents import Agent

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

agent = Agent(
    name="Calendar extractor",
    instructions="Extract calendar events from text",
    output_type=CalendarEvent,
)
```

## MCP integration (Streamable HTTP)
```python
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

async with MCPServerStreamableHttp(
    name="My HTTP Server",
    params={"url": "http://localhost:8000/mcp"},
    cache_tools_list=True,
) as server:
    agent = Agent(name="Assistant", mcp_servers=[server])
    result = await Runner.run(agent, "Your question here")
    print(result.final_output)
```

## Tracing (verified snippet)
```python
import os
from agents import set_tracing_export_api_key, Agent
from agents.extensions.models.litellm_model import LitellmModel

set_tracing_export_api_key(os.environ["OPENAI_API_KEY"])

model = LitellmModel(
    model="your-model-name",
    api_key="your-api-key",
)

agent = Agent(name="Assistant", model=model)
```
