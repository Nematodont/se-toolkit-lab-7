# Bot Development Plan

## Overview

This document describes the approach for building a Telegram bot that interfaces with an LMS (Learning Management System) backend. The bot provides slash commands for querying lab status, scores, and health checks, and later uses an LLM to understand natural language questions about the course.

## Task 1: Scaffold and Architecture

We establish a **testable handler architecture** where command logic is implemented as plain Python functions that take input and return text. These handlers have no dependency on Telegram, aiogram, or any transport layer. A `--test` CLI mode calls them directly, enabling offline verification without a Telegram connection. The project is organized into `handlers/` (command logic), `services/` (external API clients), and `config.py` (environment variable loading via pydantic-settings). This **separation of concerns** pattern means the same handler code works from `--test` mode, unit tests, and the Telegram bot.

## Task 2: Backend Integration

We will build an API client in `services/api_client.py` that queries the LMS backend using `httpx`. The `/health` command will ping the backend's health endpoint. The `/labs` command will fetch available labs. The `/scores` command will query student scores for a specific lab. All API credentials (`LMS_API_BASE_URL`, `LMS_API_KEY`) are loaded from `.env.bot.secret` via pydantic-settings, following the **configuration externalization** pattern — no secrets in code. Error handling will cover network failures, authentication errors, and unexpected responses.

## Task 3: LLM Intent Routing

Instead of regex or keyword matching, we use an LLM with **tool calling** to route natural language questions to the right handler. Each tool (e.g., `get_labs`, `get_scores`, `get_health`) has a descriptive name and description that the LLM reads to decide which to call. The quality of these descriptions is more important than prompt engineering. We will use the `LLM_API_KEY`, `LLM_API_BASE_URL`, and `LLM_API_MODEL` from the environment. The system prompt will instruct the LLM to use tools rather than answer directly. A fallback handles cases where the LLM service is unreachable.

## Task 4: Deployment

The bot runs as a Docker service alongside the backend. Key networking consideration: containers communicate via Docker service names (e.g., `backend`), not `localhost`. The `docker-compose.yml` will include the bot service with proper environment file mounting (` .env.bot.secret`). Health checks and restart policies ensure reliability. The bot process will be managed via `nohup` on the VM or as a Docker service.

## Key Architectural Decisions

- **Handler separation**: Command logic is transport-agnostic. Same functions serve CLI, tests, and Telegram.
- **pydantic-settings for config**: Type-safe configuration with automatic env var loading and .env file support.
- **Tool-calling for intent routing**: The LLM decides which tool to call based on descriptions, not hardcoded keyword matching.
- **uv + pyproject.toml**: Modern Python dependency management. No `requirements.txt`.
