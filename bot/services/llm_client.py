"""LLM client with tool calling support.

Communicates with an OpenAI-compatible LLM API to perform tool-calling
conversations. The LLM receives tool schemas, decides which to call,
and this client executes the callback for each tool and feeds results back.
"""

import json
import sys
from typing import Any, Callable

import httpx

from config import settings

# Maximum tool-call rounds to prevent infinite loops
_MAX_TOOL_ROUNDS = 5


class LLMClient:
    """Client for an OpenAI-compatible LLM API with tool calling."""

    def __init__(self) -> None:
        self.base_url = settings.llm_api_base_url.rstrip("/")
        self.api_key = settings.llm_api_key
        self.model = settings.llm_api_model

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send a chat completion request and return the raw response dict.

        Returns the first choice's message dict.
        Raises RuntimeError on API errors.
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"LLM HTTP {e.response.status_code}: {e.response.text}"
            ) from e
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected LLM response format: {e}") from e
        except httpx.RequestError as e:
            raise RuntimeError(f"LLM request failed: {e}") from e

    def route(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict[str, Any]],
        tool_callbacks: dict[str, Callable],
    ) -> str:
        """Run a tool-calling conversation loop.

        1. Send system prompt + user message + tool schemas to LLM.
        2. If LLM calls tools, execute each callback, collect results.
        3. Feed tool results back as role='tool' messages.
        4. Repeat until LLM produces a text answer (no tool calls).

        Args:
            system_prompt: System prompt instructing the LLM to use tools.
            user_message: The user's plain text query.
            tools: List of tool schema dicts (OpenAI function format).
            tool_callbacks: Map of tool name -> callable that executes it.

        Returns:
            The LLM's final text answer.
        """
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        for round_idx in range(_MAX_TOOL_ROUNDS):
            response = self.chat(messages, tools=tools)
            content = response.get("content", "")
            tool_calls = response.get("tool_calls", [])

            # If no tool calls, we have our answer
            if not tool_calls:
                return content or "I couldn't determine an answer to your question."

            # Execute each tool call
            for tc in tool_calls:
                tc_id = tc["id"]
                fn_name = tc["function"]["name"]
                fn_args_str = tc["function"].get("arguments", "{}")

                print(
                    f"[tool] LLM called: {fn_name}({fn_args_str})",
                    file=sys.stderr,
                )

                try:
                    fn_args = json.loads(fn_args_str)
                except json.JSONDecodeError:
                    fn_args = {}

                callback = tool_callbacks.get(fn_name)
                if callback:
                    try:
                        result = callback(**fn_args)
                        result_str = json.dumps(result, ensure_ascii=False, default=str)
                    except Exception as e:
                        result_str = json.dumps({"error": str(e)})
                else:
                    result_str = json.dumps({"error": f"Unknown tool: {fn_name}"})

                print(
                    f"[tool] Result: {result_str[:200]}",
                    file=sys.stderr,
                )

                # Append assistant response and tool result to conversation
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tc],
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc_id,
                        "content": result_str,
                    }
                )

            print(
                f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM (round {round_idx + 1})",
                file=sys.stderr,
            )

        # If we exhausted all rounds, ask the LLM to summarize without tools
        messages.append(
            {
                "role": "system",
                "content": "Based on the tool results above, provide a concise answer to the user's original question.",
            }
        )
        final = self.chat(messages, tools=[])
        return final.get("content", "I couldn't produce an answer after multiple attempts.")
