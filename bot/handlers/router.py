"""Command router — dispatches a command string to the appropriate handler."""

from handlers.handcomm.commands import (
    handle_health,
    handle_help,
    handle_labs,
    handle_scores,
    handle_start,
    handle_unknown,
)
from handlers.intent_router import route_intent


def route_command(text: str) -> str:
    """Parse a command string and dispatch to the appropriate handler.

    Used by both --test mode and the Telegram bot entry point.
    """
    text = text.strip()
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        handlers = {
            "/start": handle_start,
            "/help": handle_help,
            "/health": handle_health,
            "/labs": handle_labs,
            "/scores": lambda: handle_scores(args),
        }
        handler = handlers.get(cmd)
        if handler:
            return handler()
        return handle_unknown(text)
    # Plain text — use LLM intent router (Task 3)
    return route_intent(text)
