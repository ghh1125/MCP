# LangGraph MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps **LangGraph** as an MCP (Model Context Protocol) service so LLM clients can run graph-based agents, tool-calling workflows, and stateful conversations through a clean interface.

Main capabilities:
- Build and execute **stateful graphs** (`StateGraph` + compiled runtime).
- Expose **prebuilt ReAct agents** (`create_react_agent`) as MCP (Model Context Protocol) tools.
- Bridge graph tool-calling via `ToolNode`.
- Support local execution or remote LangGraph server access via `langgraph-sdk`.

---

## 2) Installation Method

Recommended dependencies:
- `langgraph`
- `langgraph-prebuilt`
- `langgraph-sdk`
- `pydantic`
- `httpx`

Install with pip:
- `pip install langgraph langgraph-prebuilt langgraph-sdk pydantic httpx`

Optional production storage/checkpoint backends:
- `langgraph-checkpoint`
- `langgraph-checkpoint-sqlite`
- `langgraph-checkpoint-postgres`
- Redis / Postgres runtime services if needed

CLI (optional, for validation/run/deploy workflows):
- `pip install langgraph-cli`

---

## 3) Quick Start

Typical integration paths:

### A. In-process graph service
1. Define typed state (Pydantic or TypedDict style).
2. Build a `StateGraph`.
3. Compile and invoke/stream with LangGraph runtime.
4. Expose invoke/stream methods as MCP (Model Context Protocol) service endpoints.

### B. Prebuilt agent service (fastest)
1. Use `create_react_agent(...)` from `langgraph-prebuilt`.
2. Register tools (or map MCP (Model Context Protocol) tools via `ToolNode`).
3. Expose chat/run methods as MCP (Model Context Protocol) endpoints.

### C. Remote mode
1. Use `langgraph_sdk.get_client()` or `get_sync_client()`.
2. Forward MCP (Model Context Protocol) requests to remote LangGraph runs/threads APIs.
3. Return normalized responses to MCP (Model Context Protocol) clients.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service surface:

- `health`
  - Basic liveness/readiness check.

- `graph.invoke`
  - Run a graph once with input/state payload.
  - Returns final output + metadata.

- `graph.stream`
  - Stream step/token/events from runtime execution.
  - Useful for interactive clients and long tasks.

- `agent.chat`
  - Chat-oriented endpoint backed by `create_react_agent`.
  - Handles conversation turns and tool usage.

- `tools.execute`
  - Execute tool calls via `ToolNode` bridge.
  - Returns tool outputs/errors in structured form.

- `threads.create` / `threads.get`
  - Create/retrieve persistent conversation thread context.

- `runs.create` / `runs.get` / `runs.cancel`
  - Manage long-running jobs (especially in remote SDK mode).

- `store.get` / `store.put` (optional)
  - Access backing store/checkpoint state where enabled.

---

## 5) Common Issues and Notes

- Version alignment:
  - Keep `langgraph`, `langgraph-prebuilt`, and `langgraph-sdk` on compatible versions.
- Checkpoint backend setup:
  - SQLite is easiest locally; Postgres is recommended for production durability.
- Streaming behavior:
  - Prefer streaming endpoints for long-running graphs to avoid timeouts.
- Tool safety:
  - Validate tool schemas and sanitize external tool I/O before exposing via MCP (Model Context Protocol).
- Performance:
  - Use async runtime paths for high concurrency.
  - Add caching/checkpointing for expensive multi-step workflows.
- Operational fallback:
  - If direct embedding is constrained, use `langgraph` CLI for app validation/build/run flows.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/langchain-ai/langgraph
- Core library (graph/runtime): `libs/langgraph`
- Prebuilt agents/tools: `libs/prebuilt`
- Python SDK (remote mode): `libs/sdk-py`
- CLI: `libs/cli`
- Checkpoint backends:
  - `libs/checkpoint`
  - `libs/checkpoint-sqlite`
  - `libs/checkpoint-postgres`

If you want, I can also generate a ready-to-use MCP (Model Context Protocol) service skeleton (endpoint contracts + minimal Python wiring) based on these modules.