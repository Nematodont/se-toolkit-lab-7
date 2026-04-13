"""Intent-based natural language router.

When the user types plain text (not a slash command), this module sends the
message to the LLM with tool definitions. The LLM decides which API tools
to call, the bot executes them, feeds results back, and the LLM produces
a natural language answer.
"""

import sys

from services.api_client import APIClient
from services.llm_client import LLMClient
from services.tool_schemas import (
    SYSTEM_PROMPT,
    TOOL_SCHEMAS,
    build_tool_callbacks,
)

# Fallback responses for common non-query messages
_GREETINGS = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening", "привет", "здравствуй"}
_CAPABILITIES_HINT = (
    "I can help you with questions about labs, scores, pass rates, groups, and students. "
    "Try asking things like:\n"
    "• What labs are available?\n"
    "• Show me scores for lab 4\n"
    "• Which lab has the lowest pass rate?\n"
    "• Who are the top 5 students?"
)


def route_intent(user_message: str) -> str:
    """Route a plain text message through the LLM intent router.

    Args:
        user_message: The user's message (not a slash command).

    Returns:
        A text response to show to the user.
    """
    text = user_message.strip().lower()

    # Handle greetings without LLM
    if text in _GREETINGS:
        return f"Hello! {_CAPABILITIES_HINT}"

    # Handle empty/gibberish
    if not text or len(text) < 2:
        return f"I didn't understand that. {_CAPABILITIES_HINT}"

    # Use the LLM for intent routing
    api_client = APIClient()
    llm_client = LLMClient()
    callbacks = build_tool_callbacks(api_client)

    try:
        response = llm_client.route(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            tools=TOOL_SCHEMAS,
            tool_callbacks=callbacks,
        )
        return response
    except RuntimeError as e:
        print(f"[intent] LLM error: {e}", file=sys.stderr)
        return (
            "Sorry, I couldn't process your request right now. "
            "The AI service may be temporarily unavailable. "
            "You can still use slash commands like /labs, /health, /scores <lab>."
        )
