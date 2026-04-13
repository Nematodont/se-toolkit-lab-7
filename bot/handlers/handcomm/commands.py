"""Slash command handlers.

Each handler is a plain function that takes optional arguments and returns a string.
No Telegram dependency — callable from --test mode, unit tests, or the bot.
"""

from services.api_client import APIClient
from handlers.keyboard import START_BUTTONS, format_buttons_html


def handle_start() -> str:
    """Handle the /start command."""
    return (
        "Welcome to the LMS bot! Use /help to see available commands.\n\n"
        + format_buttons_html(START_BUTTONS)
    )


def handle_help() -> str:
    """Handle the /help command."""
    return (
        "Available commands:\n"
        "/start — Start the bot\n"
        "/help — Show this help message\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — Show scores for a lab"
    )


def handle_health() -> str:
    """Handle the /health command — calls GET /items/ to verify backend."""
    client = APIClient()
    result = client.get("/items/")
    if isinstance(result, str):
        # Error message from the API client
        return f"Backend error: {result}"
    item_count = len(result)
    return f"Backend is healthy. {item_count} items available."


def handle_labs() -> str:
    """Handle the /labs command — lists labs from GET /items/."""
    client = APIClient()
    result = client.get("/items/")
    if isinstance(result, str):
        return f"Backend error: {result}"
    labs = [item for item in result if item.get("type") == "lab"]
    if not labs:
        return "No labs found in the backend."
    lines = ["Available labs:"]
    for lab in labs:
        lines.append(f"- {lab['title']}")
    return "\n".join(lines)


def handle_scores(args: str) -> str:
    """Handle the /scores <lab> command — per-task pass rates."""
    if not args or not args.strip():
        return "Usage: /scores <lab-id> (e.g., /scores lab-01)"
    lab_id = args.strip()
    client = APIClient()
    result = client.get(f"/analytics/pass-rates?lab={lab_id}")
    if isinstance(result, str):
        return f"Backend error: {result}"
    if not result:
        return f"No pass-rate data found for '{lab_id}'. Check the lab ID."
    lines = [f"Pass rates for {lab_id}:"]
    for entry in result:
        task_name = entry.get("task", entry.get("title", "Unknown"))
        avg = entry.get("avg_score", entry.get("pass_rate", 0))
        attempts = entry.get("attempts", 0)
        lines.append(f"- {task_name}: {avg:.1f}% ({attempts} attempts)")
    return "\n".join(lines)


def handle_unknown(command: str) -> str:
    """Handle unrecognized input."""
    if command.startswith("/"):
        return f"Unknown command: {command}. Use /help for available commands."
    # Plain text that didn't go through LLM router (fallback)
    return (
        f"I didn't understand: {command}\n\n"
        "Try asking questions like:\n"
        "• What labs are available?\n"
        "• Show me scores for lab 1\n"
        "• Which lab has the lowest pass rate?"
    )
