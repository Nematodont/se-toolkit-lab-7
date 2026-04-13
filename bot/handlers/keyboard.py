"""Inline keyboard button definitions for the Telegram bot.

Defines common query buttons that users can tap instead of typing.
These are used with aiogram's InlineKeyboardMarkup in Telegram mode,
and serve as a catalog of suggested queries in --test mode.
"""

from typing import NamedTuple


class QuickButton(NamedTuple):
    """A single inline button with display text and the query it sends."""

    text: str
    query: str


# Common queries users can tap
START_BUTTONS: list[QuickButton] = [
    QuickButton("📋 Available labs", "what labs are available?"),
    QuickButton("📊 Scores for lab 1", "show me scores for lab 1"),
    QuickButton("🏆 Top 5 students", "who are the top 5 students?"),
    QuickButton("📈 Lowest pass rate", "which lab has the lowest pass rate?"),
    QuickButton("👥 Group rankings", "show group rankings for lab 1"),
    QuickButton("🔄 Sync data", "sync data from autochecker"),
]


def format_buttons_html(buttons: list[QuickButton]) -> str:
    """Format buttons as an HTML list for --test mode display."""
    lines = ["<b>Quick queries (tap in Telegram, or try these):</b>"]
    for btn in buttons:
        lines.append(f"• <code>{btn.query}</code>")
    return "\n".join(lines)


def get_start_keyboard() -> list[list[QuickButton]]:
    """Return the keyboard layout for /start.

    Returns rows of buttons for inline keyboard construction.
    """
    # Arrange in 2-column rows
    rows: list[list[QuickButton]] = []
    for i in range(0, len(START_BUTTONS), 2):
        rows.append(START_BUTTONS[i : i + 2])
    return rows
