# Bot Development Plan

## Overview

This document describes the approach for building a Telegram bot that interfaces with an LMS (Learning Management System) backend. The bot provides slash commands for querying lab status, scores, and health checks, and later uses an LLM to understand natural language questions about the course.

## Task 1: Scaffold and Architecture

We establish a **testable handler architecture** where command logic is implemented as plain Python functions that take input and return text. These handlers have no dependency on Telegram, aiogram, or any transport layer. A `--test` CLI mode calls them directly, enabling offline verification without a Telegram connection. The project is organized into `handlers/` (command logic), `services/` (external API clients), and `config.py` (environment variable loading via pydantic-settings). This **separation of concerns** pattern means the same handler code works from `--test` mode, unit tests, and the Telegram bot.

## Task 2: Backend Integration

We will build an API client in `services/api_client.py` that queries the LMS backend using `httpx`. The `/health` command will ping the backend's health endpoint. The `/labs` command will fetch available labs. The `/scores` command will query student scores for a specific lab. All API credentials (`LMS_API_BASE_URL`, `LMS_API_KEY`) are loaded from `.env.bot.secret` via pydantic-settings, following the **configuration externalization** pattern — no secrets in code. Error handling will cover network failures, authentication errors, and unexpected responses.

## Task 3: LLM Intent Routing

Instead of regex or keyword matching, we use an LLM with **tool calling** to route natural language questions to the right handler. The architecture follows the **tool-use pattern** from Lab 6: the LLM receives tool schemas (9 backend endpoints as function schemas), a system prompt, and the user's message. It responds with tool calls, the bot executes them via `APIClient`, feeds results back as `role: tool` messages, and the LLM produces a final answer.

Key components:
- `services/llm_client.py` — LLM client with a `route()` method that runs the tool-calling loop (max 5 rounds). Debug output goes to stderr via `print(..., file=sys.stderr)`.
- `services/tool_schemas.py` — all 9 tool definitions with descriptive names and parameter schemas. Quality of descriptions directly affects routing accuracy.
- `handlers/intent_router.py` — dispatches plain text to the LLM. Handles greetings and gibberish with fallback responses without calling the LLM.
- `handlers/keyboard.py` — inline keyboard button definitions for common queries (used in Telegram mode, displayed as hints in --test mode).

The system prompt instructs the LLM to always use tools rather than guess. For multi-step queries (e.g., "which lab has the lowest pass rate?"), the LLM calls `get_items` first, then `get_pass_rates` for each lab, then compares. The tool result feedback loop is critical — each round appends tool results to the conversation and calls the LLM again.

Error handling: if the LLM service is unreachable, the router returns a friendly message suggesting slash commands as a fallback.

## Task 4: Deployment

The bot runs as a Docker service alongside the backend. Key networking consideration: containers communicate via Docker service names (e.g., `backend`), not `localhost`. The `docker-compose.yml` will include the bot service with proper environment file mounting (` .env.bot.secret`). Health checks and restart policies ensure reliability. The bot process will be managed via `nohup` on the VM or as a Docker service.

## Key Architectural Decisions

- **Handler separation**: Command logic is transport-agnostic. Same functions serve CLI, tests, and Telegram.
- **pydantic-settings for config**: Type-safe configuration with automatic env var loading and .env file support.
- **Tool-calling for intent routing**: The LLM decides which tool to call based on descriptions, not hardcoded keyword matching.
- **uv + pyproject.toml**: Modern Python dependency management. No `requirements.txt`.
