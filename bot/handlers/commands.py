"""Slash command handlers.

Each handler is a plain function that takes optional arguments and returns a string.
No Telegram dependency — callable from --test mode, unit tests, or the bot.
"""


def handle_start() -> str:
    """Handle the /start command."""
    return "Welcome to the LMS bot! Use /help to see available commands."


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
    """Handle the /health command."""
    return "Health check: not implemented yet (Task 2)"


def handle_labs() -> str:
    """Handle the /labs command."""
    return "Labs listing: not implemented yet (Task 2)"


def handle_scores(args: str) -> str:
    """Handle the /scores command."""
    return f"Scores for '{args}': not implemented yet (Task 2)"


def handle_unknown(command: str) -> str:
    """Handle unrecognized input."""
    return f"Unknown command: {command}. Use /help for available commands."
