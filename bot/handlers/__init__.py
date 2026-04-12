"""Command handlers — plain functions with no Telegram dependency."""

from handlers.commands import (
    handle_health,
    handle_help,
    handle_labs,
    handle_scores,
    handle_start,
)
from handlers.router import route_command

__all__ = [
    "handle_health",
    "handle_help",
    "handle_labs",
    "handle_scores",
    "handle_start",
    "route_command",
]
