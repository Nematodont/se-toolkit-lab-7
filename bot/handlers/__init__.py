"""Command handlers — plain functions with no Telegram dependency."""

from handlers.handcomm.commands import (
    handle_health,
    handle_help,
    handle_labs,
    handle_scores,
    handle_start,
)
from handlers.intent_router import route_intent
from handlers.keyboard import START_BUTTONS, get_start_keyboard
from handlers.router import route_command

__all__ = [
    "handle_health",
    "handle_help",
    "handle_labs",
    "handle_scores",
    "handle_start",
    "route_command",
    "route_intent",
    "START_BUTTONS",
    "get_start_keyboard",
]
