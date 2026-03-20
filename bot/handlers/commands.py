"""
Command handler implementations.

Each handler is a pure function that returns a text response.
"""


def handle_start() -> str:
    """Handle /start command."""
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command."""
    return """Available commands:
/start - Start the bot
/help - Show this help message
/health - Check backend status
/labs - List available labs
/scores - View your scores"""


def handle_health() -> str:
    """Handle /health command."""
    return "Backend status: OK (placeholder)"


def handle_labs() -> str:
    """Handle /labs command."""
    return "Available labs: Lab 01, Lab 02, Lab 03, Lab 04 (placeholder)"


def handle_scores(args: str) -> str:
    """Handle /scores command."""
    return f"Scores for {args}: No data yet (placeholder)"
