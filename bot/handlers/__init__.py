"""
Command handlers for the LMS bot.

Handlers are pure functions that take input and return text.
They don't know about Telegram - same logic works from --test mode,
unit tests, or the Telegram bot client.
"""

from .commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
